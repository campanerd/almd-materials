from tkinter import messagebox

import customtkinter

from src.models.customer import Customer
from src.services.customer_service import CustomerService, InvalidCustomerDataError


class CustomersScreen(customtkinter.CTkFrame):
    def __init__(self, master, customer_service: CustomerService):
        super().__init__(master, fg_color="transparent")
        self.customer_service = customer_service
        self.customer_id_being_edited: int | None = None

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

        buttons_panel = customtkinter.CTkFrame(form_panel, fg_color="transparent")
        buttons_panel.grid(row=1, column=2, sticky="e", padx=8, pady=(0, 8))

        self.cancel_edit_button = customtkinter.CTkButton(
            buttons_panel, text="Cancelar edição", fg_color="gray40", command=self._cancel_edit
        )

        self.save_button = customtkinter.CTkButton(
            buttons_panel, text="Cadastrar cliente", command=self._save_customer
        )
        self.save_button.pack(side="right")

    def _build_customer_list(self) -> None:
        self.customer_list_panel = customtkinter.CTkScrollableFrame(self, label_text="Clientes cadastrados")
        self.customer_list_panel.grid(row=1, column=0, sticky="nsew", padx=16, pady=(8, 16))
        self.customer_list_panel.grid_columnconfigure(0, weight=1)

    def _save_customer(self) -> None:
        try:
            if self.customer_id_being_edited is None:
                self.customer_service.register_customer(
                    full_name=self.name_field.get(),
                    address=self.address_field.get(),
                    phone_number=self.phone_field.get(),
                )
            else:
                self.customer_service.update_customer(
                    Customer(
                        id=self.customer_id_being_edited,
                        full_name=self.name_field.get(),
                        address=self.address_field.get(),
                        phone_number=self.phone_field.get(),
                    )
                )
        except InvalidCustomerDataError as error:
            self.message_label.configure(text=str(error))
            return

        self._cancel_edit()
        self.refresh_customer_list()

    def _start_editing_customer(self, customer: Customer) -> None:
        self.customer_id_being_edited = customer.id
        self.message_label.configure(text="")

        self.name_field.delete(0, "end")
        self.name_field.insert(0, customer.full_name)
        self.address_field.delete(0, "end")
        self.address_field.insert(0, customer.address)
        self.phone_field.delete(0, "end")
        self.phone_field.insert(0, customer.phone_number)

        self.save_button.configure(text="Salvar alterações")
        self.cancel_edit_button.pack(side="right", padx=(0, 8))

    def _cancel_edit(self) -> None:
        self.customer_id_being_edited = None
        self.message_label.configure(text="")
        self.name_field.delete(0, "end")
        self.address_field.delete(0, "end")
        self.phone_field.delete(0, "end")
        self.save_button.configure(text="Cadastrar cliente")
        self.cancel_edit_button.pack_forget()

    def _delete_customer(self, customer: Customer) -> None:
        confirmed = messagebox.askyesno(
            "Excluir cliente", f"Tem certeza que deseja excluir o cliente '{customer.full_name}'?"
        )
        if not confirmed:
            return

        try:
            self.customer_service.delete_customer(customer.id)
        except InvalidCustomerDataError as error:
            messagebox.showerror("Não foi possível excluir", str(error))
            return

        if self.customer_id_being_edited == customer.id:
            self._cancel_edit()
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

        edit_button = customtkinter.CTkButton(
            self.customer_list_panel, text="Editar", width=70,
            command=lambda: self._start_editing_customer(customer),
        )
        edit_button.grid(row=row_index, column=1, padx=(8, 0), pady=4)

        delete_button = customtkinter.CTkButton(
            self.customer_list_panel, text="Excluir", width=70, fg_color="firebrick3", hover_color="firebrick4",
            command=lambda: self._delete_customer(customer),
        )
        delete_button.grid(row=row_index, column=2, padx=8, pady=4)
