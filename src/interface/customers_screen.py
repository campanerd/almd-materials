import customtkinter

from src.interface import theme
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
from src.models.customer import Customer
from src.services.customer_service import CustomerService, InvalidCustomerDataError

DOUBLE_CLICK_HINT = "Clique duas vezes numa linha para editar."
COLUMN_WEIGHTS = [(4, 170), (3, 140), (5, 190), (0, 112)]
COLUMN_TITLES = ["Nome", "Telefone", "Endereço", ""]


class CustomersScreen(customtkinter.CTkFrame):
    def __init__(self, master, customer_service: CustomerService):
        super().__init__(master, fg_color="transparent")
        self.customer_service = customer_service

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self._build_registration_form()
        self._build_customer_list()

        self.refresh_customer_list()

    def _build_registration_form(self) -> None:
        card = SectionCard(self)
        card.grid(row=0, column=0, sticky="ew")
        card.grid_columnconfigure((0, 1, 2), weight=1)

        customtkinter.CTkLabel(
            card,
            text="Novo cliente",
            font=theme.font("section"),
            text_color=theme.TEXT_PRIMARY,
            anchor="w",
        ).grid(row=0, column=0, columnspan=3, sticky="ew", padx=20, pady=(18, 14))

        name_container, self.name_field = build_field(card, "Nome completo", "Ex.: Maria Silva")
        name_container.grid(row=1, column=0, sticky="ew", padx=(20, 8))

        address_container, self.address_field = build_field(card, "Endereço", "Rua, número, bairro")
        address_container.grid(row=1, column=1, sticky="ew", padx=8)

        phone_container, self.phone_field = build_field(card, "Telefone", "(00) 00000-0000")
        phone_container.grid(row=1, column=2, sticky="ew", padx=(8, 20))

        self.message_label = customtkinter.CTkLabel(
            card,
            text=DOUBLE_CLICK_HINT,
            font=theme.font("caption"),
            text_color=theme.TEXT_MUTED,
            anchor="w",
        )
        self.message_label.grid(row=2, column=0, columnspan=2, sticky="ew", padx=20, pady=(14, 18))

        register_button = build_primary_button(card, "Cadastrar cliente", self._register_customer)
        register_button.grid(row=2, column=2, sticky="e", padx=(8, 20), pady=(14, 18))

    def _build_customer_list(self) -> None:
        card = SectionCard(self)
        card.grid(row=1, column=0, sticky="nsew", pady=(18, 0))
        card.grid_columnconfigure(0, weight=1)
        card.grid_rowconfigure(0, weight=1)

        self.customer_list_panel = customtkinter.CTkScrollableFrame(
            card,
            fg_color=theme.BG_CANVAS,
            corner_radius=10,
            scrollbar_button_color=theme.SWITCH_TRACK,
            scrollbar_button_hover_color=theme.ACCENT_FG,
        )
        self.customer_list_panel.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.customer_list_panel.grid_columnconfigure(0, weight=1)

    def _show_message(self, message: str, is_error: bool) -> None:
        """The strip always carries text so the card never changes height."""
        self.message_label.configure(
            text=message or DOUBLE_CLICK_HINT,
            text_color=theme.DANGER if is_error else theme.TEXT_MUTED,
        )

    def _register_customer(self) -> None:
        try:
            self.customer_service.register_customer(
                full_name=self.name_field.get(),
                address=self.address_field.get(),
                phone_number=self.phone_field.get(),
            )
        except InvalidCustomerDataError as error:
            self._show_message(str(error), is_error=True)
            return

        self._show_message("", is_error=False)
        for field in (self.name_field, self.address_field, self.phone_field):
            field.delete(0, "end")
        self.refresh_customer_list()

    def _open_editor(self, customer: Customer) -> None:
        dialog = ModalDialog(self.winfo_toplevel(), "Editar cliente", width=520, height=430)

        name_container, name_field = build_field(dialog.body, "Nome completo")
        name_container.grid(row=0, column=0, sticky="ew", pady=(0, 14))
        name_field.insert(0, customer.full_name)

        address_container, address_field = build_field(dialog.body, "Endereço")
        address_container.grid(row=1, column=0, sticky="ew", pady=(0, 14))
        address_field.insert(0, customer.address)

        phone_container, phone_field = build_field(dialog.body, "Telefone")
        phone_container.grid(row=2, column=0, sticky="ew")
        phone_field.insert(0, customer.phone_number)

        error_label = customtkinter.CTkLabel(
            dialog.body,
            text="",
            font=theme.font("caption"),
            text_color=theme.DANGER,
            anchor="w",
            wraplength=440,
        )
        error_label.grid(row=3, column=0, sticky="ew", pady=(12, 0))

        def save() -> None:
            try:
                self.customer_service.update_customer(
                    Customer(
                        id=customer.id,
                        full_name=name_field.get(),
                        address=address_field.get(),
                        phone_number=phone_field.get(),
                    )
                )
            except InvalidCustomerDataError as error:
                error_label.configure(text=str(error))
                return

            dialog.close()
            self.refresh_customer_list()

        dialog.add_cancel_button()
        save_button = build_primary_button(dialog.footer, "Salvar alterações", save)
        save_button.configure(width=160)
        save_button.grid(row=0, column=2)

        dialog.show()

    def _delete_customer(self, customer: Customer) -> None:
        confirmed = ask_confirmation(
            self.winfo_toplevel(),
            "Excluir cliente",
            f"Tem certeza que deseja excluir o cliente '{customer.full_name}'?",
            "Excluir cliente",
        )
        if not confirmed:
            return

        try:
            self.customer_service.delete_customer(customer.id)
        except InvalidCustomerDataError as error:
            show_error(self.winfo_toplevel(), "Não foi possível excluir", str(error))
            return

        self.refresh_customer_list()

    def refresh_customer_list(self) -> None:
        for widget in self.customer_list_panel.winfo_children():
            widget.destroy()

        customers = self.customer_service.list_all_customers()
        if not customers:
            EmptyState(
                self.customer_list_panel,
                "Nenhum cliente cadastrado ainda.",
                "Use o formulário acima para cadastrar o primeiro.",
            ).grid(row=0, column=0, sticky="ew")
            return

        build_list_header(self.customer_list_panel, COLUMN_WEIGHTS, COLUMN_TITLES).grid(
            row=0, column=0, sticky="ew", pady=(0, 4)
        )

        rows = [self._build_customer_row(index, customer) for index, customer in enumerate(customers)]
        animate_rows_entrance(rows)

    def _build_customer_row(self, index: int, customer: Customer) -> DataRow:
        row = DataRow(
            self.customer_list_panel,
            COLUMN_WEIGHTS,
            on_activate=lambda: self._open_editor(customer),
        )
        row.grid(row=index + 1, column=0, sticky="ew", pady=2)

        customtkinter.CTkLabel(
            row,
            text=customer.full_name,
            font=theme.font("body_strong"),
            text_color=theme.TEXT_PRIMARY,
            anchor="w",
        ).grid(row=0, column=1, sticky="ew", padx=(0, 12))

        customtkinter.CTkLabel(
            row,
            text=customer.phone_number,
            font=theme.font("numeric"),
            text_color=theme.TEXT_SECONDARY,
            anchor="w",
        ).grid(row=0, column=2, sticky="ew", padx=(0, 12))

        customtkinter.CTkLabel(
            row,
            text=customer.address,
            font=theme.font("body"),
            text_color=theme.TEXT_SECONDARY,
            anchor="w",
        ).grid(row=0, column=3, sticky="ew", padx=(0, 12))

        build_danger_button(row, "Excluir", lambda: self._delete_customer(customer)).grid(
            row=0, column=4, padx=(0, 12)
        )

        row.finish_setup()
        return row

    def repaint_for_theme_change(self) -> None:
        """Hover tweens leave literal colors on the rows, which would freeze across an
        appearance change, so the list is rebuilt from the current tokens."""
        self.refresh_customer_list()
