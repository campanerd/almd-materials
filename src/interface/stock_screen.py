from tkinter import filedialog

import customtkinter
from PIL import Image

from src.models.stock_item import StockItem
from src.services.stock_item_service import InvalidStockItemDataError, StockItemService

THUMBNAIL_SIZE = (52, 52)

SURFACE = "#FFFFFF"
PANEL = "#F8FBF9"
PRIMARY_GREEN = "#176B45"
PRIMARY_GREEN_HOVER = "#12583A"
ACCENT_GREEN = "#4FA373"
SECONDARY_GREEN = "#E7F3EB"
SECONDARY_GREEN_HOVER = "#D9EBDD"
BORDER = "#D9E5DE"
TEXT = "#17352A"
MUTED_TEXT = "#708079"
PLACEHOLDER = "#8B9893"
ERROR = "#C2413A"
ROW_HOVER = "#F1F7F3"


class StockScreen(customtkinter.CTkFrame):
    def __init__(self, master, stock_item_service: StockItemService):
        super().__init__(master, fg_color=SURFACE)
        self.stock_item_service = stock_item_service
        self.selected_image_path: str | None = None
        self._thumbnail_images: list[customtkinter.CTkImage] = []

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self._build_page_header()
        self._build_registration_form()
        self._build_item_list()

        self.refresh_item_list()

    def _entry_style(self) -> dict:
        return {
            "height": 46,
            "corner_radius": 10,
            "border_width": 1,
            "border_color": BORDER,
            "fg_color": SURFACE,
            "text_color": TEXT,
            "placeholder_text_color": PLACEHOLDER,
            "font": customtkinter.CTkFont(family="Segoe UI", size=13),
        }

    def _build_page_header(self) -> None:
        header = customtkinter.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=22, pady=(20, 8))
        header.grid_columnconfigure(0, weight=1)

        customtkinter.CTkLabel(
            header,
            text="Controle de estoque",
            text_color=TEXT,
            anchor="w",
            font=customtkinter.CTkFont(family="Segoe UI", size=25, weight="bold"),
        ).grid(row=0, column=0, sticky="w")

        customtkinter.CTkLabel(
            header,
            text="Organize os materiais, quantidades, preços e imagens cadastradas.",
            text_color=MUTED_TEXT,
            anchor="w",
            font=customtkinter.CTkFont(family="Segoe UI", size=12),
        ).grid(row=1, column=0, sticky="w", pady=(2, 0))

        customtkinter.CTkFrame(
            header,
            height=4,
            width=54,
            corner_radius=2,
            fg_color=ACCENT_GREEN,
        ).grid(row=2, column=0, sticky="w", pady=(10, 0))

    def _build_registration_form(self) -> None:
        form_panel = customtkinter.CTkFrame(
            self,
            fg_color=PANEL,
            corner_radius=16,
            border_width=1,
            border_color=BORDER,
        )
        form_panel.grid(row=1, column=0, sticky="ew", padx=22, pady=(8, 10))
        form_panel.grid_columnconfigure((0, 1), weight=1)

        customtkinter.CTkFrame(
            form_panel,
            height=4,
            corner_radius=2,
            fg_color=PRIMARY_GREEN,
        ).grid(row=0, column=0, columnspan=2, sticky="ew", padx=18, pady=(14, 0))

        customtkinter.CTkLabel(
            form_panel,
            text="Novo item",
            text_color=TEXT,
            anchor="w",
            font=customtkinter.CTkFont(family="Segoe UI", size=15, weight="bold"),
        ).grid(row=1, column=0, columnspan=2, sticky="w", padx=18, pady=(12, 8))

        self.name_field = customtkinter.CTkEntry(
            form_panel,
            placeholder_text="Nome do item",
            **self._entry_style(),
        )
        self.name_field.grid(row=2, column=0, sticky="ew", padx=(18, 8), pady=(0, 8))

        self.description_field = customtkinter.CTkEntry(
            form_panel,
            placeholder_text="Descrição",
            **self._entry_style(),
        )
        self.description_field.grid(row=2, column=1, sticky="ew", padx=(8, 18), pady=(0, 8))

        self.quantity_field = customtkinter.CTkEntry(
            form_panel,
            placeholder_text="Quantidade",
            **self._entry_style(),
        )
        self.quantity_field.grid(row=3, column=0, sticky="ew", padx=(18, 8), pady=8)

        self.price_field = customtkinter.CTkEntry(
            form_panel,
            placeholder_text="Preço unitário (R$)",
            **self._entry_style(),
        )
        self.price_field.grid(row=3, column=1, sticky="ew", padx=(8, 18), pady=8)

        choose_image_button = customtkinter.CTkButton(
            form_panel,
            text="Escolher imagem",
            command=self._choose_image,
            height=44,
            corner_radius=10,
            fg_color=SECONDARY_GREEN,
            hover_color=SECONDARY_GREEN_HOVER,
            text_color=PRIMARY_GREEN,
            border_width=1,
            border_color="#CBE1D3",
            font=customtkinter.CTkFont(family="Segoe UI", size=13, weight="bold"),
        )
        choose_image_button.grid(row=4, column=0, sticky="w", padx=(18, 8), pady=(8, 18))

        self.chosen_image_label = customtkinter.CTkLabel(
            form_panel,
            text="Nenhuma imagem escolhida",
            text_color=MUTED_TEXT,
            anchor="w",
            font=customtkinter.CTkFont(family="Segoe UI", size=12),
        )
        self.chosen_image_label.grid(row=4, column=0, sticky="ew", padx=(170, 8), pady=(8, 18))

        register_button = customtkinter.CTkButton(
            form_panel,
            text="Cadastrar item",
            command=self._register_item,
            height=44,
            corner_radius=10,
            fg_color=PRIMARY_GREEN,
            hover_color=PRIMARY_GREEN_HOVER,
            text_color="#FFFFFF",
            font=customtkinter.CTkFont(family="Segoe UI", size=13, weight="bold"),
        )
        register_button.grid(row=4, column=1, sticky="e", padx=(8, 18), pady=(8, 18))

        self.message_label = customtkinter.CTkLabel(
            form_panel,
            text="",
            text_color=ERROR,
            anchor="w",
            font=customtkinter.CTkFont(family="Segoe UI", size=12),
        )
        self.message_label.grid(row=5, column=0, columnspan=2, sticky="ew", padx=18, pady=(0, 12))

    def _build_item_list(self) -> None:
        self.item_list_panel = customtkinter.CTkScrollableFrame(
            self,
            label_text="Itens em estoque",
            label_font=customtkinter.CTkFont(family="Segoe UI", size=15, weight="bold"),
            label_text_color=TEXT,
            label_fg_color=SURFACE,
            fg_color=SURFACE,
            corner_radius=16,
            border_width=1,
            border_color=BORDER,
            scrollbar_button_color="#B8C9BF",
            scrollbar_button_hover_color="#91A99B",
        )
        self.item_list_panel.grid(row=2, column=0, sticky="nsew", padx=22, pady=(10, 22))
        self.item_list_panel.grid_columnconfigure(1, weight=1)

    def _choose_image(self) -> None:
        chosen_path = filedialog.askopenfilename(
            title="Escolha a imagem do item",
            filetypes=[("Imagens", "*.png *.jpg *.jpeg *.gif *.webp")],
        )
        if chosen_path:
            self.selected_image_path = chosen_path
            self.chosen_image_label.configure(text=chosen_path.replace("\\", "/").split("/")[-1])

    def _register_item(self) -> None:
        try:
            quantity = int(self.quantity_field.get() or 0)
            price = float((self.price_field.get() or "0").replace(",", "."))
            self.stock_item_service.register_item(
                name=self.name_field.get(),
                description=self.description_field.get(),
                quantity_in_stock=quantity,
                unit_price=price,
                original_image_path=self.selected_image_path,
            )
        except (InvalidStockItemDataError, ValueError) as error:
            self.message_label.configure(text=str(error) or "Verifique os valores de quantidade e preço.")
            return

        self.message_label.configure(text="")
        self.name_field.delete(0, "end")
        self.description_field.delete(0, "end")
        self.quantity_field.delete(0, "end")
        self.price_field.delete(0, "end")
        self.selected_image_path = None
        self.chosen_image_label.configure(text="Nenhuma imagem escolhida")
        self.refresh_item_list()

    def refresh_item_list(self) -> None:
        for widget in self.item_list_panel.winfo_children():
            widget.destroy()
        self._thumbnail_images.clear()

        items = self.stock_item_service.list_all_items()
        if not items:
            customtkinter.CTkLabel(
                self.item_list_panel,
                text="Nenhum item cadastrado ainda.",
                text_color=MUTED_TEXT,
                anchor="w",
                font=customtkinter.CTkFont(family="Segoe UI", size=13),
            ).grid(row=0, column=0, columnspan=2, sticky="ew", padx=14, pady=18)
            return

        for row_index, item in enumerate(items):
            self._add_item_row(row_index, item)

    def _add_item_row(self, row_index: int, item: StockItem) -> None:
        row_color = SURFACE if row_index % 2 == 0 else ROW_HOVER
        thumbnail = self._load_thumbnail(item.image_path)

        customtkinter.CTkLabel(
            self.item_list_panel,
            image=thumbnail,
            text="",
            width=68,
            height=64,
            corner_radius=9,
            fg_color=row_color,
        ).grid(row=row_index, column=0, sticky="nsew", padx=(8, 0), pady=3)

        text = (
            f"{item.name}     •     {item.quantity_in_stock} un.     •     "
            f"R$ {item.unit_price:.2f}     •     {item.description}"
        )
        customtkinter.CTkLabel(
            self.item_list_panel,
            text=text,
            anchor="w",
            justify="left",
            height=64,
            corner_radius=9,
            fg_color=row_color,
            text_color=TEXT,
            font=customtkinter.CTkFont(family="Segoe UI", size=13),
        ).grid(row=row_index, column=1, sticky="nsew", padx=(0, 8), pady=3)

    def _load_thumbnail(self, image_path: str | None) -> customtkinter.CTkImage:
        if image_path:
            try:
                image = Image.open(image_path)
            except (FileNotFoundError, OSError):
                image = Image.new("RGB", THUMBNAIL_SIZE, color="#DCE5DF")
        else:
            image = Image.new("RGB", THUMBNAIL_SIZE, color="#DCE5DF")

        thumbnail = customtkinter.CTkImage(light_image=image, dark_image=image, size=THUMBNAIL_SIZE)
        self._thumbnail_images.append(thumbnail)
        return thumbnail
