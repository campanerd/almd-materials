from tkinter import filedialog, messagebox

import customtkinter
from PIL import Image

from src.models.stock_item import StockItem
from src.services.stock_item_service import InvalidStockItemDataError, StockItemService

THUMBNAIL_SIZE = (48, 48)


class StockScreen(customtkinter.CTkFrame):
    def __init__(self, master, stock_item_service: StockItemService):
        super().__init__(master, fg_color="transparent")
        self.stock_item_service = stock_item_service
        self.selected_image_path: str | None = None
        self.item_id_being_edited: int | None = None
        self.existing_image_path_being_edited: str | None = None
        self._thumbnail_images: list[customtkinter.CTkImage] = []

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self._build_registration_form()
        self._build_item_list()

        self.refresh_item_list()

    def _build_registration_form(self) -> None:
        form_panel = customtkinter.CTkFrame(self, corner_radius=12)
        form_panel.grid(row=0, column=0, sticky="ew", padx=16, pady=(16, 8))
        form_panel.grid_columnconfigure((0, 1, 2, 3), weight=1)

        self.name_field = customtkinter.CTkEntry(form_panel, placeholder_text="Nome do item")
        self.name_field.grid(row=0, column=0, sticky="ew", padx=8, pady=8)

        self.description_field = customtkinter.CTkEntry(form_panel, placeholder_text="Descrição")
        self.description_field.grid(row=0, column=1, sticky="ew", padx=8, pady=8)

        self.quantity_field = customtkinter.CTkEntry(form_panel, placeholder_text="Quantidade")
        self.quantity_field.grid(row=0, column=2, sticky="ew", padx=8, pady=8)

        self.price_field = customtkinter.CTkEntry(form_panel, placeholder_text="Preço unitário (R$)")
        self.price_field.grid(row=0, column=3, sticky="ew", padx=8, pady=8)

        choose_image_button = customtkinter.CTkButton(
            form_panel, text="Escolher imagem", command=self._choose_image
        )
        choose_image_button.grid(row=1, column=0, sticky="w", padx=8, pady=(0, 8))

        self.chosen_image_label = customtkinter.CTkLabel(form_panel, text="Nenhuma imagem escolhida")
        self.chosen_image_label.grid(row=1, column=1, sticky="w", padx=8, pady=(0, 8))

        self.message_label = customtkinter.CTkLabel(form_panel, text="", text_color="tomato")
        self.message_label.grid(row=2, column=0, columnspan=3, sticky="w", padx=8)

        buttons_panel = customtkinter.CTkFrame(form_panel, fg_color="transparent")
        buttons_panel.grid(row=1, column=3, rowspan=2, sticky="e", padx=8, pady=(0, 8))

        self.cancel_edit_button = customtkinter.CTkButton(
            buttons_panel, text="Cancelar edição", fg_color="gray40", command=self._cancel_edit
        )

        self.save_button = customtkinter.CTkButton(
            buttons_panel, text="Cadastrar item", command=self._save_item
        )
        self.save_button.pack(side="right")

    def _build_item_list(self) -> None:
        self.item_list_panel = customtkinter.CTkScrollableFrame(self, label_text="Itens em estoque")
        self.item_list_panel.grid(row=1, column=0, sticky="nsew", padx=16, pady=(8, 16))
        self.item_list_panel.grid_columnconfigure(1, weight=1)

    def _choose_image(self) -> None:
        chosen_path = filedialog.askopenfilename(
            title="Escolha a imagem do item",
            filetypes=[("Imagens", "*.png *.jpg *.jpeg *.gif *.webp")],
        )
        if chosen_path:
            self.selected_image_path = chosen_path
            self.chosen_image_label.configure(text=chosen_path.split("/")[-1])

    def _save_item(self) -> None:
        try:
            quantity = int(self.quantity_field.get() or 0)
            price = float((self.price_field.get() or "0").replace(",", "."))

            if self.item_id_being_edited is None:
                self.stock_item_service.register_item(
                    name=self.name_field.get(),
                    description=self.description_field.get(),
                    quantity_in_stock=quantity,
                    unit_price=price,
                    original_image_path=self.selected_image_path,
                )
            else:
                image_path = self.existing_image_path_being_edited
                if self.selected_image_path:
                    image_path = self.stock_item_service.copy_image_to_data_folder(self.selected_image_path)

                self.stock_item_service.update_item(
                    StockItem(
                        id=self.item_id_being_edited,
                        name=self.name_field.get(),
                        description=self.description_field.get(),
                        quantity_in_stock=quantity,
                        unit_price=price,
                        image_path=image_path,
                    )
                )
        except (InvalidStockItemDataError, ValueError) as error:
            self.message_label.configure(text=str(error) or "Verifique os valores de quantidade e preço.")
            return

        self._cancel_edit()
        self.refresh_item_list()

    def _start_editing_item(self, item: StockItem) -> None:
        self.item_id_being_edited = item.id
        self.existing_image_path_being_edited = item.image_path
        self.selected_image_path = None
        self.message_label.configure(text="")

        self.name_field.delete(0, "end")
        self.name_field.insert(0, item.name)
        self.description_field.delete(0, "end")
        self.description_field.insert(0, item.description)
        self.quantity_field.delete(0, "end")
        self.quantity_field.insert(0, str(item.quantity_in_stock))
        self.price_field.delete(0, "end")
        self.price_field.insert(0, f"{item.unit_price:.2f}")
        self.chosen_image_label.configure(
            text="Imagem atual mantida (escolha outra para substituir)" if item.image_path else "Nenhuma imagem escolhida"
        )

        self.save_button.configure(text="Salvar alterações")
        self.cancel_edit_button.pack(side="right", padx=(0, 8))

    def _cancel_edit(self) -> None:
        self.item_id_being_edited = None
        self.existing_image_path_being_edited = None
        self.message_label.configure(text="")
        self.name_field.delete(0, "end")
        self.description_field.delete(0, "end")
        self.quantity_field.delete(0, "end")
        self.price_field.delete(0, "end")
        self.selected_image_path = None
        self.chosen_image_label.configure(text="Nenhuma imagem escolhida")
        self.save_button.configure(text="Cadastrar item")
        self.cancel_edit_button.pack_forget()

    def _delete_item(self, item: StockItem) -> None:
        confirmed = messagebox.askyesno("Excluir item", f"Tem certeza que deseja excluir o item '{item.name}'?")
        if not confirmed:
            return

        try:
            self.stock_item_service.delete_item(item.id)
        except InvalidStockItemDataError as error:
            messagebox.showerror("Não foi possível excluir", str(error))
            return

        if self.item_id_being_edited == item.id:
            self._cancel_edit()
        self.refresh_item_list()

    def refresh_item_list(self) -> None:
        for widget in self.item_list_panel.winfo_children():
            widget.destroy()
        self._thumbnail_images.clear()

        items = self.stock_item_service.list_all_items()
        if not items:
            customtkinter.CTkLabel(self.item_list_panel, text="Nenhum item cadastrado ainda.").grid(
                row=0, column=0, sticky="w", padx=8, pady=8
            )
            return

        for row_index, item in enumerate(items):
            self._add_item_row(row_index, item)

    def _add_item_row(self, row_index: int, item: StockItem) -> None:
        thumbnail = self._load_thumbnail(item.image_path)
        customtkinter.CTkLabel(self.item_list_panel, image=thumbnail, text="").grid(
            row=row_index, column=0, padx=8, pady=4
        )

        text = (
            f"{item.name}  •  {item.quantity_in_stock} un.  •  "
            f"R$ {item.unit_price:.2f}  •  {item.description}"
        )
        customtkinter.CTkLabel(self.item_list_panel, text=text, anchor="w").grid(
            row=row_index, column=1, sticky="ew", padx=8, pady=4
        )

        edit_button = customtkinter.CTkButton(
            self.item_list_panel, text="Editar", width=70,
            command=lambda: self._start_editing_item(item),
        )
        edit_button.grid(row=row_index, column=2, padx=(8, 0), pady=4)

        delete_button = customtkinter.CTkButton(
            self.item_list_panel, text="Excluir", width=70, fg_color="firebrick3", hover_color="firebrick4",
            command=lambda: self._delete_item(item),
        )
        delete_button.grid(row=row_index, column=3, padx=8, pady=4)

    def _load_thumbnail(self, image_path: str | None) -> customtkinter.CTkImage:
        if image_path:
            try:
                image = Image.open(image_path)
            except (FileNotFoundError, OSError):
                image = Image.new("RGB", THUMBNAIL_SIZE, color="gray")
        else:
            image = Image.new("RGB", THUMBNAIL_SIZE, color="gray")

        thumbnail = customtkinter.CTkImage(light_image=image, dark_image=image, size=THUMBNAIL_SIZE)
        self._thumbnail_images.append(thumbnail)
        return thumbnail
