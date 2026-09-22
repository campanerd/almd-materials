import customtkinter

from src.models.customer import Customer
from src.services.customer_service import CustomerService, InvalidCustomerDataError


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
        form_panel = customtkinter.CTkFrame(self, corner_radius=12)
        form_panel.grid(row=0, column=0, sticky="ew", padx=16, pady=(16, 8))
        form_panel.grid_columnconfigure((0, 1, 2), weight=1)

        self.name_field = customtkinter.CTkEntry(form_panel, placeholder_text="Nome completo")
        self.name_field.grid(row=0, column=0, sticky="ew", padx=8, pady=8)

        self.address_field = customtkinter.CTkEntry(form_panel, placeholder_text="Endereço")
        self.address_field.grid(row=0, column=1, sticky="ew", padx=8, pady=8)

        self.phone_field = customtkinter.CTkEntry(form_panel, placeholder_text="Telefone")
        self.phone_field.grid(row=0, column=2, sticky="ew", padx=8, pady=8)

        self.message_label = customtkinter.CTkLabel(form_panel, text="", text_color="tomato")
        self.message_label.grid(row=1, column=0, columnspan=2, sticky="w", padx=8)

        register_button = customtkinter.CTkButton(
            form_panel, text="Cadastrar cliente", command=self._register_customer
        )
        register_button.grid(row=1, column=2, sticky="e", padx=8, pady=(0, 8))

    def _build_customer_list(self) -> None:
        self.customer_list_panel = customtkinter.CTkScrollableFrame(self, label_text="Clientes cadastrados")
        self.customer_list_panel.grid(row=1, column=0, sticky="nsew", padx=16, pady=(8, 16))
        self.customer_list_panel.grid_columnconfigure(0, weight=1)

    def _register_customer(self) -> None:
        try:
            self.customer_service.register_customer(
                full_name=self.name_field.get(),
                address=self.address_field.get(),
                phone_number=self.phone_field.get(),
            )
        except InvalidCustomerDataError as error:
            self.message_label.configure(text=str(error))
            return

        self.message_label.configure(text="")
        self.name_field.delete(0, "end")
        self.address_field.delete(0, "end")
        self.phone_field.delete(0, "end")
        self.refresh_customer_list()

    def refresh_customer_list(self) -> None:
        for widget in self.customer_list_panel.winfo_children():
            widget.destroy()

        customers = self.customer_service.list_all_customers()
        if not customers:
            customtkinter.CTkLabel(self.customer_list_panel, text="Nenhum cliente cadastrado ainda.").grid(
                row=0, column=0, sticky="w", padx=8, pady=8
            )
            return

        for row_index, customer in enumerate(customers):
            self._add_customer_row(row_index, customer)

    def _add_customer_row(self, row_index: int, customer: Customer) -> None:
        text = f"{customer.full_name}  •  {customer.phone_number}  •  {customer.address}"
        customtkinter.CTkLabel(self.customer_list_panel, text=text, anchor="w").grid(
            row=row_index, column=0, sticky="ew", padx=8, pady=4
        )
