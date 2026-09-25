from __future__ import annotations

import re
import webbrowser
from pathlib import Path
from urllib.parse import quote

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    Image,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from src.app_paths import persistent_data_path, resource_path
from src.models.customer import Customer
from src.models.sale import Sale


RECEIPTS_FOLDER = persistent_data_path("receipts")
LOGO_PATH = resource_path("assets", "logo.png")
BRAND_GREEN = colors.HexColor("#12592F")
SOFT_GREEN = colors.HexColor("#EAF0EC")
TEXT_DARK = colors.HexColor("#14211B")
TEXT_MUTED = colors.HexColor("#5E6F66")
BORDER = colors.HexColor("#DCE5E0")


class ReceiptError(Exception):
    pass


class WhatsAppPhoneError(ReceiptError):
    pass


def format_currency(amount: float) -> str:
    grouped = f"{amount:,.2f}"
    return "R$ " + grouped.replace(",", "|").replace(".", ",").replace("|", ".")


def normalize_brazilian_whatsapp_number(phone_number: str) -> str:
    digits = re.sub(r"\D", "", phone_number)
    if len(digits) in (10, 11):
        return "55" + digits
    if len(digits) in (12, 13) and digits.startswith("55"):
        return digits
    raise WhatsAppPhoneError(
        "O telefone do cliente precisa ter DDD para abrir a conversa no WhatsApp."
    )


class ReceiptService:
    def __init__(self, receipts_folder: Path = RECEIPTS_FOLDER):
        self.receipts_folder = Path(receipts_folder)

    def generate_pdf(
        self,
        sale: Sale,
        customer: Customer,
        item_name_by_id: dict[int, str],
    ) -> Path:
        try:
            self.receipts_folder.mkdir(parents=True, exist_ok=True)
            sale_identifier = sale.id if sale.id is not None else sale.sale_date_time.strftime("%Y%m%d%H%M%S")
            output_path = self.receipts_folder / f"recibo_venda_{sale_identifier}.pdf"
            self._build_document(output_path, sale, customer, item_name_by_id)
            return output_path
        except OSError as error:
            raise ReceiptError("Não foi possível salvar o recibo em PDF.") from error
        except Exception as error:
            if isinstance(error, ReceiptError):
                raise
            raise ReceiptError("Não foi possível gerar o recibo em PDF.") from error

    def open_whatsapp(self, customer: Customer) -> None:
        number = normalize_brazilian_whatsapp_number(customer.phone_number)
        first_name = customer.full_name.strip().split()[0] if customer.full_name.strip() else "cliente"
        message = (
            f"Olá, {first_name}! Sua compra na Almeida Materiais foi finalizada. "
            "Segue o recibo da sua compra."
        )
        url = f"https://wa.me/{number}?text={quote(message)}"
        if not webbrowser.open(url):
            raise ReceiptError("Não foi possível abrir o WhatsApp no navegador.")

    def _build_document(
        self,
        output_path: Path,
        sale: Sale,
        customer: Customer,
        item_name_by_id: dict[int, str],
    ) -> None:
        doc = SimpleDocTemplate(
            str(output_path),
            pagesize=A4,
            rightMargin=22 * mm,
            leftMargin=22 * mm,
            topMargin=18 * mm,
            bottomMargin=18 * mm,
            title=f"Recibo da venda {sale.id or ''}".strip(),
            author="Almeida Materiais",
        )

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            "ReceiptTitle",
            parent=styles["Heading1"],
            fontName="Helvetica-Bold",
            fontSize=18,
            leading=22,
            textColor=TEXT_DARK,
            spaceAfter=2 * mm,
        )
        body_style = ParagraphStyle(
            "ReceiptBody",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=9.5,
            leading=13,
            textColor=TEXT_DARK,
        )
        muted_style = ParagraphStyle(
            "ReceiptMuted",
            parent=body_style,
            textColor=TEXT_MUTED,
        )
        right_style = ParagraphStyle(
            "ReceiptRight",
            parent=body_style,
            alignment=TA_RIGHT,
        )
        thanks_style = ParagraphStyle(
            "ReceiptThanks",
            parent=body_style,
            alignment=TA_CENTER,
            textColor=TEXT_MUTED,
        )

        story = []
        if LOGO_PATH.is_file():
            logo = Image(str(LOGO_PATH), width=18 * mm, height=18 * mm)
            logo.hAlign = "LEFT"
            story.append(logo)
            story.append(Spacer(1, 2 * mm))

        story.append(Paragraph("ALMEIDA MATERIAIS", title_style))
        story.append(Paragraph("Comprovante de venda", muted_style))
        story.append(Spacer(1, 7 * mm))

        metadata = [
            [Paragraph("Cliente", muted_style), Paragraph(customer.full_name, body_style)],
            [Paragraph("Telefone", muted_style), Paragraph(customer.phone_number, body_style)],
            [Paragraph("Data", muted_style), Paragraph(sale.sale_date_time.strftime("%d/%m/%Y às %H:%M"), body_style)],
            [Paragraph("Venda", muted_style), Paragraph(f"#{sale.id}" if sale.id is not None else "-", body_style)],
        ]
        metadata_table = Table(metadata, colWidths=[32 * mm, 118 * mm], hAlign="LEFT")
        metadata_table.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("LINEBELOW", (0, -1), (-1, -1), 0.5, BORDER),
        ]))
        story.append(metadata_table)
        story.append(Spacer(1, 8 * mm))

        item_rows = [["ITEM", "QTD.", "UNITÁRIO", "SUBTOTAL"]]
        for sold_item in sale.sold_items:
            item_rows.append([
                item_name_by_id.get(sold_item.stock_item_id, f"Item #{sold_item.stock_item_id}"),
                str(sold_item.quantity_sold),
                format_currency(sold_item.unit_price_at_sale_time),
                format_currency(sold_item.total_value),
            ])

        items_table = Table(
            item_rows,
            colWidths=[70 * mm, 18 * mm, 31 * mm, 31 * mm],
            repeatRows=1,
            hAlign="LEFT",
        )
        items_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), SOFT_GREEN),
            ("TEXTCOLOR", (0, 0), (-1, 0), BRAND_GREEN),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 8.5),
            ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 1), (-1, -1), 9),
            ("TEXTCOLOR", (0, 1), (-1, -1), TEXT_DARK),
            ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ("LINEBELOW", (0, 0), (-1, -1), 0.5, BORDER),
        ]))
        story.append(items_table)
        story.append(Spacer(1, 7 * mm))

        total_table = Table(
            [[Paragraph("TOTAL", muted_style), Paragraph(f"<b>{format_currency(sale.total_amount)}</b>", right_style)]],
            colWidths=[75 * mm, 75 * mm],
            hAlign="LEFT",
        )
        total_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), SOFT_GREEN),
            ("BOX", (0, 0), (-1, -1), 0.7, BORDER),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 10),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
            ("LEFTPADDING", (0, 0), (-1, -1), 10),
            ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ]))
        story.append(total_table)
        story.append(Spacer(1, 12 * mm))
        story.append(Paragraph("Obrigado pela preferência!", thanks_style))

        doc.build(story)
