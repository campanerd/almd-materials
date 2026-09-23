import customtkinter

from src.models.customer import Customer
from src.services.customer_service import CustomerService, InvalidCustomerDataError

SURFACE = "#FFFFFF"
PANEL = "#F8FBF9"
PRIMARY_GREEN = "#176B45"
PRIMARY_GREEN_HOVER = "#12583A"
ACCENT_GREEN = "#4FA373"
SOFT_GREEN = "#EAF5EE"
BORDER = "#D9E5DE"
TEXT = "#17352A"
MUTED_TEXT = "#708079"
PLACEHOLDER = "#8B9893"
ERROR = "#C2413A"
ROW_HOVER = "#F1F7F3"


class CustomersScreen(customtkinter.CTkFrame):
    def __init__(self, master, customer_service: CustomerService):
        super().__init__(master, fg_color=SURFACE)
        self.customer_service = customer_service

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self._build_page_header()
        self._build_registration_form()
        self._build_customer_list()

        self.refresh_customer_list()

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
            text="Gestão de clientes",
            text_color=TEXT,
            anchor="w",
            font=customtkinter.CTkFont(family="Segoe UI", size=25, weight="bold"),
        ).grid(row=0, column=0, sticky="w")

        customtkinter.CTkLabel(
            header,
            text="Cadastre e consulte os clientes registrados no sistema.",
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
        form_panel.grid_columnconfigure((0, 1, 2), weight=1)

        customtkinter.CTkFrame(
            form_panel,
            height=4,
            corner_radius=2,
            fg_color=PRIMARY_GREEN,
        ).grid(row=0, column=0, columnspan=3, sticky="ew", padx=18, pady=(14, 0))

        customtkinter.CTkLabel(
            form_panel,
            text="Novo cliente",
            text_color=TEXT,
            anchor="w",
            font=customtkinter.CTkFont(family="Segoe UI", size=15, weight="bold"),
        ).grid(row=1, column=0, columnspan=3, sticky="w", padx=18, pady=(12, 8))

        self.name_field = customtkinter.CTkEntry(
            form_panel,
            placeholder_text="Nome completo",
            **self._entry_style(),
        )
        self.name_field.grid(row=2, column=0, columnspan=2, sticky="ew", padx=(18, 8), pady=(0, 8))

        self.phone_field = customtkinter.CTkEntry(
            form_panel,
            placeholder_text="Telefone",
            **self._entry_style(),
        )
        self.phone_field.grid(row=2, column=2, sticky="ew", padx=(8, 18), pady=(0, 8))

        self.address_field = customtkinter.CTkEntry(
            form_panel,
            placeholder_text="Endereço",
            **self._entry_style(),
        )
        self.address_field.grid(row=3, column=0, columnspan=2, sticky="ew", padx=(18, 8), pady=(8, 18))

        register_button = customtkinter.CTkButton(
            form_panel,
            text="Cadastrar cliente",
            command=self._register_customer,
            height=46,
            corner_radius=10,
            fg_color=PRIMARY_GREEN,
            hover_color=PRIMARY_GREEN_HOVER,
            text_color="#FFFFFF",
            font=customtkinter.CTkFont(family="Segoe UI", size=13, weight="bold"),
        )
        register_button.grid(row=3, column=2, sticky="ew", padx=(8, 18), pady=(8, 18))

        self.message_label = customtkinter.CTkLabel(
            form_panel,
            text="",
            text_color=ERROR,
            anchor="w",
            font=customtkinter.CTkFont(family="Segoe UI", size=12),
        )
        self.message_label.grid(row=4, column=0, columnspan=3, sticky="ew", padx=18, pady=(0, 12))

    def _build_customer_list(self) -> None:
        self.customer_list_panel = customtkinter.CTkScrollableFrame(
            self,
            label_text="Clientes cadastrados",
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
        self.customer_list_panel.grid(row=2, column=0, sticky="nsew", padx=22, pady=(10, 22))
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
            customtkinter.CTkLabel(
                self.customer_list_panel,
                text="Nenhum cliente cadastrado ainda.",
                text_color=MUTED_TEXT,
                anchor="w",
                font=customtkinter.CTkFont(family="Segoe UI", size=13),
            ).grid(row=0, column=0, sticky="ew", padx=14, pady=18)
            return

        for row_index, customer in enumerate(customers):
            self._add_customer_row(row_index, customer)

    def _add_customer_row(self, row_index: int, customer: Customer) -> None:
        text = f"{customer.full_name}     •     {customer.phone_number}     •     {customer.address}"
        customtkinter.CTkLabel(
            self.customer_list_panel,
            text=text,
            anchor="w",
            justify="left",
            height=48,
            corner_radius=9,
            fg_color=SURFACE if row_index % 2 == 0 else ROW_HOVER,
            text_color=TEXT,
            font=customtkinter.CTkFont(family="Segoe UI", size=13),
        ).grid(row=row_index, column=0, sticky="ew", padx=8, pady=3)
