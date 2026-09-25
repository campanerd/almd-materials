from datetime import datetime

import pytest

from src.models.customer import Customer
from src.models.sale import Sale, SoldItem
from src.services.receipt_service import (
    ReceiptService,
    WhatsAppPhoneError,
    normalize_brazilian_whatsapp_number,
)


def test_normalize_brazilian_whatsapp_number_adds_country_code():
    assert normalize_brazilian_whatsapp_number("(11) 99999-8888") == "5511999998888"


def test_normalize_brazilian_whatsapp_number_rejects_phone_without_area_code():
    with pytest.raises(WhatsAppPhoneError):
        normalize_brazilian_whatsapp_number("99999-8888")


def test_generate_pdf_creates_receipt_file(tmp_path):
    customer = Customer(
        full_name="Davi Almeida",
        address="Rua A, 10",
        phone_number="(11) 99999-8888",
        id=1,
    )
    sale = Sale(
        customer_id=1,
        sold_items=[SoldItem(stock_item_id=10, quantity_sold=2, unit_price_at_sale_time=39.9)],
        sale_date_time=datetime(2026, 9, 25, 14, 30),
        id=42,
    )

    path = ReceiptService(tmp_path).generate_pdf(sale, customer, {10: "Cimento CP-II"})

    assert path.exists()
    assert path.suffix == ".pdf"
    assert path.stat().st_size > 0


def test_open_whatsapp_uses_customer_phone_and_prefilled_message(monkeypatch, tmp_path):
    opened_urls = []
    monkeypatch.setattr("src.services.receipt_service.webbrowser.open", lambda url: opened_urls.append(url) or True)
    customer = Customer(
        full_name="Davi Almeida",
        address="Rua A, 10",
        phone_number="(11) 99999-8888",
        id=1,
    )

    ReceiptService(tmp_path).open_whatsapp(customer)

    assert opened_urls
    assert opened_urls[0].startswith("https://wa.me/5511999998888?text=")
    assert "Davi" in opened_urls[0]
