from pathlib import Path
from tkinter import filedialog

import customtkinter
from PIL import Image, ImageDraw, ImageFont

from src.interface import theme
from src.interface.animation import resolve_color
from src.interface.components import (
    DataRow,
    EmptyState,
    SectionCard,
    animate_rows_entrance,
    build_danger_button,
    build_field,
    build_list_header,
    build_primary_button,
)
from src.interface.dialogs import ModalDialog, ask_confirmation, show_error
from src.models.stock_item import StockItem
from src.services.stock_item_service import InvalidStockItemDataError, StockItemService

DOUBLE_CLICK_HINT = "Clique duas vezes numa linha para editar."
NO_IMAGE_CHOSEN_MESSAGE = "Nenhuma imagem escolhida"
IMAGE_KEPT_MESSAGE = "Imagem atual mantida (escolha outra para substituir)"
INVALID_NUMBER_MESSAGE = "Quantidade e preço devem ser números válidos."

OUT_OF_STOCK_CHIP_TEXT = "sem estoque"
LOW_STOCK_CHIP_TEXT = "estoque baixo"
LOW_STOCK_THRESHOLD = 10

THUMBNAIL_SIZE = (40, 40)
# The stock chip gets a column of its own: sharing the quantity column made the
# uniform sizing clip it to "ESTOQUE BAI".
COLUMN_WEIGHTS = [(0, 56), (4, 150), (1, 90), (0, 124), (2, 104), (4, 170), (0, 112)]
COLUMN_TITLES = ["", "Item", "Qtd.", "", "Preço unitário", "Descrição", ""]


def _load_placeholder_font():
    try:
        return ImageFont.truetype("segoeui.ttf", 20)
    except OSError:
        return ImageFont.load_default()


def format_price_as_number(unit_price: float) -> str:
    return f"{unit_price:.2f}".replace(".", ",")


def format_price_with_currency(unit_price: float) -> str:
    return f"R$ {format_price_as_number(unit_price)}"


def ask_for_image_path() -> str:
    return filedialog.askopenfilename(
        title="Escolha a imagem do item",
        filetypes=[("Imagens", "*.png *.jpg *.jpeg *.gif *.webp")],
    )


def build_secondary_button(master, text: str, command) -> customtkinter.CTkButton:
    """The design system ships a primary and a danger button only; picking an image is
    a side errand that sits next to the primary action and must not compete with it."""
    return customtkinter.CTkButton(
        master,
        text=text,
        command=command,
        height=38,
        corner_radius=theme.CONTROL_RADIUS,
        fg_color="transparent",
        hover_color=theme.ROW_HOVER,
        text_color=theme.TEXT_SECONDARY,
        border_width=1,
        border_color=theme.BORDER,
        font=theme.font("body"),
    )


def build_stock_level_chip(master, quantity_in_stock: int) -> customtkinter.CTkLabel | None:
    if quantity_in_stock == 0:
        chip_text, fill_color, text_color = (
            OUT_OF_STOCK_CHIP_TEXT,
            theme.CHIP_DANGER,
            theme.CHIP_DANGER_TEXT,
        )
    elif quantity_in_stock < LOW_STOCK_THRESHOLD:
        chip_text, fill_color, text_color = (
            LOW_STOCK_CHIP_TEXT,
            theme.CHIP_WARN,
            theme.CHIP_WARN_TEXT,
        )
    else:
        return None

    return customtkinter.CTkLabel(
        master,
        text=chip_text.upper(),
        font=theme.font("overline"),
        fg_color=fill_color,
        text_color=text_color,
        corner_radius=8,
        padx=8,
        pady=2,
    )


class StockScreen(customtkinter.CTkFrame):
    def __init__(self, master, stock_item_service: StockItemService):
        super().__init__(master, fg_color="transparent")
        self.stock_item_service = stock_item_service
        self.selected_image_path: str | None = None
        self._thumbnail_images: list[customtkinter.CTkImage] = []

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self._build_registration_form()
        self._build_item_list()

        self.refresh_item_list()

    def _build_registration_form(self) -> None:
        card = SectionCard(self)
        card.grid(row=0, column=0, sticky="ew")
        card.grid_columnconfigure(0, weight=3)
        card.grid_columnconfigure(1, weight=3)
        card.grid_columnconfigure(2, weight=1, minsize=120)
        card.grid_columnconfigure(3, weight=1, minsize=140)

        customtkinter.CTkLabel(
            card,
            text="Novo item",
            font=theme.font("section"),
            text_color=theme.TEXT_PRIMARY,
            anchor="w",
        ).grid(row=0, column=0, columnspan=4, sticky="ew", padx=20, pady=(18, 14))

        name_container, self.name_field = build_field(card, "Nome do item", "Ex.: Cimento CP-II 50kg")
        name_container.grid(row=1, column=0, sticky="ew", padx=(20, 8))

        description_container, self.description_field = build_field(card, "Descrição", "Marca, medida, observações")
        description_container.grid(row=1, column=1, sticky="ew", padx=8)

        quantity_container, self.quantity_field = build_field(card, "Quantidade", "0")
        quantity_container.grid(row=1, column=2, sticky="ew", padx=8)

        price_container, self.price_field = build_field(card, "Preço unitário (R$)", "0,00")
        price_container.grid(row=1, column=3, sticky="ew", padx=(8, 20))

        image_row = customtkinter.CTkFrame(card, fg_color="transparent")
        image_row.grid(row=2, column=0, columnspan=4, sticky="ew", padx=20, pady=(14, 0))
        image_row.grid_columnconfigure(1, weight=1)

        build_secondary_button(image_row, "Escolher imagem", self._choose_image).grid(row=0, column=0)

        self.chosen_image_label = customtkinter.CTkLabel(
            image_row,
            text=NO_IMAGE_CHOSEN_MESSAGE,
            font=theme.font("caption"),
            text_color=theme.TEXT_MUTED,
            anchor="w",
        )
        self.chosen_image_label.grid(row=0, column=1, sticky="ew", padx=(12, 0))

        self.message_label = customtkinter.CTkLabel(
            card,
            text=DOUBLE_CLICK_HINT,
            font=theme.font("caption"),
            text_color=theme.TEXT_MUTED,
            anchor="w",
        )
        self.message_label.grid(row=3, column=0, columnspan=3, sticky="ew", padx=20, pady=(14, 18))

        register_button = build_primary_button(card, "Cadastrar item", self._register_item)
        register_button.grid(row=3, column=3, sticky="e", padx=(8, 20), pady=(14, 18))

    def _build_item_list(self) -> None:
        card = SectionCard(self)
        card.grid(row=1, column=0, sticky="nsew", pady=(18, 0))
        card.grid_columnconfigure(0, weight=1)
        card.grid_rowconfigure(0, weight=1)

        self.item_list_panel = customtkinter.CTkScrollableFrame(
            card,
            fg_color=theme.BG_CANVAS,
            corner_radius=10,
            scrollbar_button_color=theme.SWITCH_TRACK,
            scrollbar_button_hover_color=theme.ACCENT_FG,
        )
        self.item_list_panel.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.item_list_panel.grid_columnconfigure(0, weight=1)

    def _show_message(self, message: str, is_error: bool) -> None:
        """The strip always carries text so the card never changes height."""
        self.message_label.configure(
            text=message or DOUBLE_CLICK_HINT,
            text_color=theme.DANGER if is_error else theme.TEXT_MUTED,
        )

    def _choose_image(self) -> None:
        chosen_path = ask_for_image_path()
        if chosen_path:
            self.selected_image_path = chosen_path
            self.chosen_image_label.configure(text=Path(chosen_path).name)

    def _register_item(self) -> None:
        # Parsing is kept apart from the service validation: merging the two excepts
        # leaks the raw ValueError text into the interface.
        try:
            quantity_in_stock = int(self.quantity_field.get() or 0)
            unit_price = float((self.price_field.get() or "0").replace(",", "."))
        except ValueError:
            self._show_message(INVALID_NUMBER_MESSAGE, is_error=True)
            return

        try:
            self.stock_item_service.register_item(
                name=self.name_field.get(),
                description=self.description_field.get(),
                quantity_in_stock=quantity_in_stock,
                unit_price=unit_price,
                original_image_path=self.selected_image_path,
            )
        except InvalidStockItemDataError as error:
            self._show_message(str(error), is_error=True)
            return

        self._clear_registration_form()
        self._show_message("", is_error=False)
        self.refresh_item_list()

    def _clear_registration_form(self) -> None:
        for field in (self.name_field, self.description_field, self.quantity_field, self.price_field):
            field.delete(0, "end")
        self.selected_image_path = None
        self.chosen_image_label.configure(text=NO_IMAGE_CHOSEN_MESSAGE)

    def _open_editor(self, item: StockItem) -> None:
        dialog = ModalDialog(self.winfo_toplevel(), "Editar item", width=560, height=500)
        newly_chosen_image_path: str | None = None

        name_container, name_field = build_field(dialog.body, "Nome do item")
        name_container.grid(row=0, column=0, sticky="ew", pady=(0, 14))
        name_field.insert(0, item.name)

        description_container, description_field = build_field(dialog.body, "Descrição")
        description_container.grid(row=1, column=0, sticky="ew", pady=(0, 14))
        description_field.insert(0, item.description)

        numbers_row = customtkinter.CTkFrame(dialog.body, fg_color="transparent")
        numbers_row.grid(row=2, column=0, sticky="ew")
        numbers_row.grid_columnconfigure((0, 1), weight=1)

        quantity_container, quantity_field = build_field(numbers_row, "Quantidade")
        quantity_container.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        quantity_field.insert(0, str(item.quantity_in_stock))

        price_container, price_field = build_field(numbers_row, "Preço unitário (R$)")
        price_container.grid(row=0, column=1, sticky="ew", padx=(8, 0))
        price_field.insert(0, format_price_as_number(item.unit_price))

        image_row = customtkinter.CTkFrame(dialog.body, fg_color="transparent")
        image_row.grid(row=3, column=0, sticky="ew", pady=(14, 0))
        image_row.grid_columnconfigure(1, weight=1)

        chosen_image_label = customtkinter.CTkLabel(
            image_row,
            text=IMAGE_KEPT_MESSAGE if item.image_path else NO_IMAGE_CHOSEN_MESSAGE,
            font=theme.font("caption"),
            text_color=theme.TEXT_MUTED,
            anchor="w",
            wraplength=300,
        )
        chosen_image_label.grid(row=0, column=1, sticky="ew", padx=(12, 0))

        error_label = customtkinter.CTkLabel(
            dialog.body,
            text="",
            font=theme.font("caption"),
            text_color=theme.DANGER,
            anchor="w",
            wraplength=480,
        )
        error_label.grid(row=4, column=0, sticky="ew", pady=(12, 0))

        def choose_another_image() -> None:
            nonlocal newly_chosen_image_path
            chosen_path = ask_for_image_path()
            if chosen_path:
                newly_chosen_image_path = chosen_path
                chosen_image_label.configure(text=Path(chosen_path).name)

        build_secondary_button(image_row, "Escolher imagem", choose_another_image).grid(row=0, column=0)

        def save() -> None:
            try:
                quantity_in_stock = int(quantity_field.get() or 0)
                unit_price = float((price_field.get() or "0").replace(",", "."))
            except ValueError:
                error_label.configure(text=INVALID_NUMBER_MESSAGE)
                return

            try:
                image_path = item.image_path
                if newly_chosen_image_path:
                    image_path = self.stock_item_service.copy_image_to_data_folder(newly_chosen_image_path)

                self.stock_item_service.update_item(
                    StockItem(
                        id=item.id,
                        name=name_field.get(),
                        description=description_field.get(),
                        quantity_in_stock=quantity_in_stock,
                        unit_price=unit_price,
                        image_path=image_path,
                    )
                )
            except InvalidStockItemDataError as error:
                error_label.configure(text=str(error))
                return

            dialog.close()
            self.refresh_item_list()

        dialog.add_cancel_button()
        save_button = build_primary_button(dialog.footer, "Salvar alterações", save)
        save_button.configure(width=160)
        save_button.grid(row=0, column=2)

        dialog.show()

    def _delete_item(self, item: StockItem) -> None:
        confirmed = ask_confirmation(
            self.winfo_toplevel(),
            "Excluir item",
            f"Tem certeza que deseja excluir o item '{item.name}'?",
            "Excluir item",
        )
        if not confirmed:
            return

        try:
            self.stock_item_service.delete_item(item.id)
        except InvalidStockItemDataError as error:
            show_error(self.winfo_toplevel(), "Não foi possível excluir", str(error))
            return

        self.refresh_item_list()

    def refresh_item_list(self) -> None:
        for widget in self.item_list_panel.winfo_children():
            widget.destroy()
        self._thumbnail_images.clear()

        items = self.stock_item_service.list_all_items()
        if not items:
            EmptyState(
                self.item_list_panel,
                "Nenhum item cadastrado ainda.",
                "Use o formulário acima para cadastrar o primeiro.",
            ).grid(row=0, column=0, sticky="ew")
            return

        build_list_header(self.item_list_panel, COLUMN_WEIGHTS, COLUMN_TITLES).grid(
            row=0, column=0, sticky="ew", pady=(0, 4)
        )

        rows = [self._build_item_row(index, item) for index, item in enumerate(items)]
        animate_rows_entrance(rows)

    def _build_item_row(self, index: int, item: StockItem) -> DataRow:
        row = DataRow(
            self.item_list_panel,
            COLUMN_WEIGHTS,
            on_activate=lambda: self._open_editor(item),
        )
        row.grid(row=index + 1, column=0, sticky="ew", pady=2)

        customtkinter.CTkLabel(
            row, image=self._load_thumbnail(item.image_path, item.name), text=""
        ).grid(row=0, column=1, padx=(0, 12))

        customtkinter.CTkLabel(
            row,
            text=item.name,
            font=theme.font("body_strong"),
            text_color=theme.TEXT_PRIMARY,
            anchor="w",
        ).grid(row=0, column=2, sticky="ew", padx=(0, 12))

        customtkinter.CTkLabel(
            row,
            text=f"{item.quantity_in_stock} un.",
            font=theme.font("numeric"),
            text_color=theme.TEXT_SECONDARY,
            anchor="w",
        ).grid(row=0, column=3, sticky="ew", padx=(0, 8))

        stock_level_chip = build_stock_level_chip(row, item.quantity_in_stock)
        if stock_level_chip is not None:
            stock_level_chip.grid(row=0, column=4, sticky="w", padx=(0, 12))

        customtkinter.CTkLabel(
            row,
            text=format_price_with_currency(item.unit_price),
            font=theme.font("numeric"),
            text_color=theme.TEXT_PRIMARY,
            anchor="w",
        ).grid(row=0, column=5, sticky="ew", padx=(0, 12))

        customtkinter.CTkLabel(
            row,
            text=item.description,
            font=theme.font("body"),
            text_color=theme.TEXT_SECONDARY,
            anchor="w",
        ).grid(row=0, column=6, sticky="ew", padx=(0, 12))

        build_danger_button(row, "Excluir", lambda: self._delete_item(item)).grid(
            row=0, column=7, padx=(0, 12)
        )

        row.finish_setup()
        return row

    def _load_thumbnail(self, image_path: str | None, item_name: str = "") -> customtkinter.CTkImage:
        """CTkImage is garbage collected the moment nothing references it and the row
        then renders blank, so every thumbnail is kept in a list on the screen."""
        image = None
        if image_path:
            try:
                image = Image.open(image_path)
            except (FileNotFoundError, OSError):
                image = None

        if image is None:
            image = self._build_initial_placeholder(item_name)

        thumbnail = customtkinter.CTkImage(light_image=image, dark_image=image, size=THUMBNAIL_SIZE)
        self._thumbnail_images.append(thumbnail)
        return thumbnail

    @staticmethod
    def _build_initial_placeholder(item_name: str) -> Image.Image:
        """An item with no photo gets its initial instead of an empty square, which
        reads as a missing image rather than a deliberate blank."""
        # PIL takes a single color, so both tones are resolved for the current
        # appearance mode; repaint_for_theme_change rebuilds them after a switch.
        placeholder = Image.new("RGB", THUMBNAIL_SIZE, color=resolve_color(theme.THUMB_BG))
        initial = item_name.strip()[:1].upper()
        if not initial:
            return placeholder

        canvas = ImageDraw.Draw(placeholder)
        canvas.text(
            (THUMBNAIL_SIZE[0] / 2, THUMBNAIL_SIZE[1] / 2),
            initial,
            fill=resolve_color(theme.TEXT_MUTED),
            anchor="mm",
            font=_load_placeholder_font(),
        )
        return placeholder

    def repaint_for_theme_change(self) -> None:
        """Hover tweens leave literal colors on the rows, which would freeze across an
        appearance change, so the list is rebuilt from the current tokens."""
        self.refresh_item_list()
