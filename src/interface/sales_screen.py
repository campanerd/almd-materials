import customtkinter

from src.services.customer_service import CustomerService
from src.services.stock_item_service import StockItemService
from src.services.sale_service import (
    InsufficientStockError,
    InvalidSaleDataError,
    ItemToSell,
    SaleService,
)

NO_CUSTOMER_SELECTED = "Selecione um cliente"
NO_ITEM_SELECTED = "Selecione um item"

SURFACE = "#FFFFFF"
PANEL = "#F8FBF9"
PRIMARY_GREEN = "#176B45"
PRIMARY_GREEN_HOVER = "#12583A"
ACCENT_GREEN = "#4FA373"
SOFT_GREEN = "#E7F3EB"
BORDER = "#D9E5DE"
TEXT = "#17352A"
MUTED_TEXT = "#708079"
PLACEHOLDER = "#8B9893"
ERROR = "#C2413A"
ROW_HOVER = "#F1F7F3"


class SalesScreen(customtkinter.CTkFrame):
    def __init__(
        self,
        master,
        customer_service: CustomerService,
        stock_item_service: StockItemService,
        sale_service: SaleService,
    ):
        super().__init__(master, fg_color=SURFACE)
        self.customer_service = customer_service
        self.stock_item_service = stock_item_service
        self.sale_service = sale_service

        self.customer_id_by_name: dict[str, int] = {}
        self.item_id_by_name: dict[str, int] = {}
        self.current_cart_items: list[ItemToSell] = []

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self._build_page_header()
        self._build_sales_workspace()
        self._build_bottom_panel()

        self.refresh_customer_and_item_options()

    def _option_menu_style(self) -> dict:
        return {
            "height": 46,
            "corner_radius": 10,
            "fg_color": SURFACE,
            "button_color": SOFT_GREEN,
            "button_hover_color": "#D9EBDD",
            "text_color": TEXT,
            "dropdown_fg_color": SURFACE,
            "dropdown_hover_color": SOFT_GREEN,
            "dropdown_text_color": TEXT,
            "font": customtkinter.CTkFont(family="Segoe UI", size=13),
            "dropdown_font": customtkinter.CTkFont(family="Segoe UI", size=13),
        }

    def _build_page_header(self) -> None:
        header = customtkinter.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=24, pady=(22, 14))
        header.grid_columnconfigure(0, weight=1)

        customtkinter.CTkLabel(
            header,
            text="Registro de vendas",
            text_color=TEXT,
            anchor="w",
            font=customtkinter.CTkFont(family="Segoe UI", size=25, weight="bold"),
        ).grid(row=0, column=0, sticky="w")

        customtkinter.CTkLabel(
            header,
            text="Selecione o cliente, monte a venda e acompanhe o histórico de compras.",
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

    def _build_sales_workspace(self) -> None:
        workspace = customtkinter.CTkFrame(self, fg_color="transparent")
        workspace.grid(row=1, column=0, sticky="nsew", padx=24, pady=(0, 12))
        workspace.grid_rowconfigure(0, weight=1)
        workspace.grid_columnconfigure(0, weight=6, uniform="sales_workspace")
        workspace.grid_columnconfigure(1, weight=5, uniform="sales_workspace")

        left_column = customtkinter.CTkFrame(workspace, fg_color="transparent")
        left_column.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        left_column.grid_columnconfigure(0, weight=1)
        left_column.grid_rowconfigure(2, weight=1)

        self._build_customer_selection(left_column)
        self._build_item_addition(left_column)
        self._build_cart(left_column)
        self._build_history(workspace)

    def _build_customer_selection(self, master) -> None:
        panel = customtkinter.CTkFrame(
            master,
            fg_color=PANEL,
            corner_radius=16,
            border_width=1,
            border_color=BORDER,
        )
        panel.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        panel.grid_columnconfigure(1, weight=1)

        customtkinter.CTkFrame(
            panel,
            width=4,
            height=60,
            corner_radius=2,
            fg_color=ACCENT_GREEN,
        ).grid(row=0, column=0, sticky="ns", padx=(14, 12), pady=12)

        content = customtkinter.CTkFrame(panel, fg_color="transparent")
        content.grid(row=0, column=1, sticky="ew", padx=(0, 16), pady=12)
        content.grid_columnconfigure(0, weight=1)

        customtkinter.CTkLabel(
            content,
            text="Cliente da venda",
            text_color=TEXT,
            anchor="w",
            font=customtkinter.CTkFont(family="Segoe UI", size=13, weight="bold"),
        ).grid(row=0, column=0, sticky="w", pady=(0, 6))

        self.customer_menu = customtkinter.CTkOptionMenu(
            content,
            values=[NO_CUSTOMER_SELECTED],
            command=self._on_customer_selected,
            **self._option_menu_style(),
        )
        self.customer_menu.grid(row=1, column=0, sticky="ew")

    def _build_item_addition(self, master) -> None:
        panel = customtkinter.CTkFrame(
            master,
            fg_color=PANEL,
            corner_radius=16,
            border_width=1,
            border_color=BORDER,
        )
        panel.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        panel.grid_columnconfigure(0, weight=1)

        customtkinter.CTkLabel(
            panel,
            text="Adicionar item",
            text_color=TEXT,
            anchor="w",
            font=customtkinter.CTkFont(family="Segoe UI", size=13, weight="bold"),
        ).grid(row=0, column=0, columnspan=3, sticky="w", padx=18, pady=(14, 8))

        self.item_menu = customtkinter.CTkOptionMenu(
            panel,
            values=[NO_ITEM_SELECTED],
            **self._option_menu_style(),
        )
        self.item_menu.grid(row=1, column=0, sticky="ew", padx=(18, 7), pady=(0, 10))

        self.quantity_field = customtkinter.CTkEntry(
            panel,
            placeholder_text="Quantidade",
            width=125,
            height=46,
            corner_radius=10,
            border_width=1,
            border_color=BORDER,
            fg_color=SURFACE,
            text_color=TEXT,
            placeholder_text_color=PLACEHOLDER,
            font=customtkinter.CTkFont(family="Segoe UI", size=13),
        )
        self.quantity_field.grid(row=1, column=1, padx=7, pady=(0, 10))

        add_button = customtkinter.CTkButton(
            panel,
            text="Adicionar à venda",
            command=self._add_item_to_cart,
            width=148,
            height=46,
            corner_radius=10,
            fg_color=PRIMARY_GREEN,
            hover_color=PRIMARY_GREEN_HOVER,
            text_color="#FFFFFF",
            font=customtkinter.CTkFont(family="Segoe UI", size=13, weight="bold"),
        )
        add_button.grid(row=1, column=2, padx=(7, 18), pady=(0, 10))

        self.message_label = customtkinter.CTkLabel(
            panel,
            text="",
            text_color=ERROR,
            anchor="w",
            font=customtkinter.CTkFont(family="Segoe UI", size=12),
        )
        self.message_label.grid(row=2, column=0, columnspan=3, sticky="ew", padx=18, pady=(0, 10))

    def _scroll_style(self) -> dict:
        return {
            "label_font": customtkinter.CTkFont(family="Segoe UI", size=15, weight="bold"),
            "label_text_color": TEXT,
            "label_fg_color": SURFACE,
            "fg_color": SURFACE,
            "corner_radius": 16,
            "border_width": 1,
            "border_color": BORDER,
            "scrollbar_button_color": "#B8C9BF",
            "scrollbar_button_hover_color": "#91A99B",
        }

    def _build_cart(self, master) -> None:
        self.cart_panel = customtkinter.CTkScrollableFrame(
            master,
            label_text="Itens desta venda",
            **self._scroll_style(),
        )
        self.cart_panel.grid(row=2, column=0, sticky="nsew")
        self.cart_panel.grid_columnconfigure(0, weight=1)

    def _build_history(self, master) -> None:
        self.history_panel = customtkinter.CTkScrollableFrame(
            master,
            label_text="Histórico de compras do cliente",
            **self._scroll_style(),
        )
        self.history_panel.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        self.history_panel.grid_columnconfigure(0, weight=1)

    def _build_bottom_panel(self) -> None:
        bottom_panel = customtkinter.CTkFrame(
            self,
            fg_color="#F3F8F5",
            corner_radius=16,
            border_width=1,
            border_color=BORDER,
        )
        bottom_panel.grid(row=2, column=0, sticky="ew", padx=24, pady=(0, 22))
        bottom_panel.grid_columnconfigure(0, weight=1)

        total_group = customtkinter.CTkFrame(bottom_panel, fg_color="transparent")
        total_group.grid(row=0, column=0, sticky="w", padx=20, pady=13)

        customtkinter.CTkLabel(
            total_group,
            text="TOTAL DA VENDA",
            text_color=MUTED_TEXT,
            anchor="w",
            font=customtkinter.CTkFont(family="Segoe UI", size=10, weight="bold"),
        ).grid(row=0, column=0, sticky="w")

        self.total_label = customtkinter.CTkLabel(
            total_group,
            text="Total: R$ 0,00",
            text_color=PRIMARY_GREEN,
            font=customtkinter.CTkFont(family="Segoe UI", size=21, weight="bold"),
        )
        self.total_label.grid(row=1, column=0, sticky="w", pady=(1, 0))

        finalize_button = customtkinter.CTkButton(
            bottom_panel,
            text="Finalizar venda",
            command=self._finalize_sale,
            width=160,
            height=48,
            corner_radius=11,
            fg_color=PRIMARY_GREEN,
            hover_color=PRIMARY_GREEN_HOVER,
            text_color="#FFFFFF",
            font=customtkinter.CTkFont(family="Segoe UI", size=13, weight="bold"),
        )
        finalize_button.grid(row=0, column=1, sticky="e", padx=18, pady=13)

    def refresh_customer_and_item_options(self) -> None:
        customers = self.customer_service.list_all_customers()
        self.customer_id_by_name = {customer.full_name: customer.id for customer in customers}
        customer_names = list(self.customer_id_by_name) or [NO_CUSTOMER_SELECTED]
        self.customer_menu.configure(values=customer_names)
        self.customer_menu.set(customer_names[0])
        self._on_customer_selected(customer_names[0])

        items = self.stock_item_service.list_all_items()
        self.item_id_by_name = {
            f"{item.name} (estoque: {item.quantity_in_stock})": item.id for item in items
        }
        item_names = list(self.item_id_by_name) or [NO_ITEM_SELECTED]
        self.item_menu.configure(values=item_names)
        self.item_menu.set(item_names[0])

    def _on_customer_selected(self, _selected_customer_name: str) -> None:
        self._refresh_selected_customer_history()

    def _add_item_to_cart(self) -> None:
        selected_item_name = self.item_menu.get()
        item_id = self.item_id_by_name.get(selected_item_name)

        if item_id is None:
            self.message_label.configure(text="Cadastre ao menos um item em estoque antes de vender.")
            return

        try:
            quantity = int(self.quantity_field.get())
            if quantity <= 0:
                raise ValueError
        except ValueError:
            self.message_label.configure(text="Informe uma quantidade válida.")
            return

        self.message_label.configure(text="")
        self.current_cart_items.append(ItemToSell(stock_item_id=item_id, desired_quantity=quantity))
        self.quantity_field.delete(0, "end")
        self._refresh_cart_display()

    def _refresh_cart_display(self) -> None:
        for widget in self.cart_panel.winfo_children():
            widget.destroy()

        item_name_by_id = {item_id: name for name, item_id in self.item_id_by_name.items()}
        stock_items_by_id = {item.id: item for item in self.stock_item_service.list_all_items()}

        sale_total = 0.0
        for row_index, item_to_sell in enumerate(self.current_cart_items):
            stock_item = stock_items_by_id.get(item_to_sell.stock_item_id)
            unit_price = stock_item.unit_price if stock_item else 0.0
            subtotal = unit_price * item_to_sell.desired_quantity
            sale_total += subtotal

            item_name = item_name_by_id.get(item_to_sell.stock_item_id, "Item")
            text = f"{item_name}     × {item_to_sell.desired_quantity}     •     R$ {subtotal:.2f}"
            customtkinter.CTkLabel(
                self.cart_panel,
                text=text,
                anchor="w",
                justify="left",
                height=46,
                corner_radius=9,
                fg_color=SURFACE if row_index % 2 == 0 else ROW_HOVER,
                text_color=TEXT,
                font=customtkinter.CTkFont(family="Segoe UI", size=13),
            ).grid(row=row_index, column=0, sticky="ew", padx=8, pady=3)

        self.total_label.configure(text=f"Total: R$ {sale_total:.2f}")

    def _refresh_selected_customer_history(self) -> None:
        for widget in self.history_panel.winfo_children():
            widget.destroy()

        selected_customer_name = self.customer_menu.get()
        customer_id = self.customer_id_by_name.get(selected_customer_name)
        if customer_id is None:
            return

        previous_sales = self.sale_service.list_purchase_history_by_customer(customer_id)
        if not previous_sales:
            customtkinter.CTkLabel(
                self.history_panel,
                text="Nenhuma compra registrada ainda.",
                text_color=MUTED_TEXT,
                anchor="w",
                font=customtkinter.CTkFont(family="Segoe UI", size=13),
            ).grid(row=0, column=0, sticky="ew", padx=14, pady=18)
            return

        for row_index, sale in enumerate(previous_sales):
            formatted_date = sale.sale_date_time.strftime("%d/%m/%Y %H:%M")
            text = (
                f"{formatted_date}     •     {len(sale.sold_items)} item(ns)     •     "
                f"R$ {sale.total_amount:.2f}"
            )
            customtkinter.CTkLabel(
                self.history_panel,
                text=text,
                anchor="w",
                justify="left",
                height=46,
                corner_radius=9,
                fg_color=SURFACE if row_index % 2 == 0 else ROW_HOVER,
                text_color=TEXT,
                font=customtkinter.CTkFont(family="Segoe UI", size=13),
            ).grid(row=row_index, column=0, sticky="ew", padx=8, pady=3)

    def _finalize_sale(self) -> None:
        selected_customer_name = self.customer_menu.get()
        customer_id = self.customer_id_by_name.get(selected_customer_name)

        if customer_id is None:
            self.message_label.configure(text="Cadastre ao menos um cliente antes de vender.")
            return
        if not self.current_cart_items:
            self.message_label.configure(text="Adicione ao menos um item à venda.")
            return

        try:
            self.sale_service.register_sale(customer_id, self.current_cart_items)
        except (InvalidSaleDataError, InsufficientStockError) as error:
            self.message_label.configure(text=str(error))
            return

        self.message_label.configure(text="")
        self.current_cart_items = []
        self._refresh_cart_display()
        self.refresh_customer_and_item_options()
        self._refresh_selected_customer_history()
