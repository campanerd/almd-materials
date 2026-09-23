from tkinter import messagebox

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


class SalesScreen(customtkinter.CTkFrame):
    def __init__(
        self,
        master,
        customer_service: CustomerService,
        stock_item_service: StockItemService,
        sale_service: SaleService,
    ):
        super().__init__(master, fg_color="transparent")
        self.customer_service = customer_service
        self.stock_item_service = stock_item_service
        self.sale_service = sale_service

        self.customer_id_by_name: dict[str, int] = {}
        self.item_id_by_name: dict[str, int] = {}
        self.current_cart_items: list[ItemToSell] = []

        self.grid_columnconfigure((0, 1), weight=1)
        self.grid_rowconfigure(2, weight=1)

        self._build_customer_selection()
        self._build_item_addition()
        self._build_cart_and_history()

        self.refresh_customer_and_item_options()

    def _build_customer_selection(self) -> None:
        panel = customtkinter.CTkFrame(self, corner_radius=12)
        panel.grid(row=0, column=0, columnspan=2, sticky="ew", padx=16, pady=(16, 8))
        panel.grid_columnconfigure(1, weight=1)

        customtkinter.CTkLabel(panel, text="Cliente:").grid(row=0, column=0, padx=8, pady=8)

        self.customer_menu = customtkinter.CTkOptionMenu(
            panel, values=[NO_CUSTOMER_SELECTED], command=self._on_customer_selected
        )
        self.customer_menu.grid(row=0, column=1, sticky="ew", padx=8, pady=8)

    def _build_item_addition(self) -> None:
        panel = customtkinter.CTkFrame(self, corner_radius=12)
        panel.grid(row=1, column=0, columnspan=2, sticky="ew", padx=16, pady=8)
        panel.grid_columnconfigure(0, weight=1)

        self.item_menu = customtkinter.CTkOptionMenu(panel, values=[NO_ITEM_SELECTED])
        self.item_menu.grid(row=0, column=0, sticky="ew", padx=8, pady=8)

        self.quantity_field = customtkinter.CTkEntry(panel, placeholder_text="Quantidade", width=100)
        self.quantity_field.grid(row=0, column=1, padx=8, pady=8)

        add_button = customtkinter.CTkButton(
            panel, text="Adicionar à venda", command=self._add_item_to_cart
        )
        add_button.grid(row=0, column=2, padx=8, pady=8)

        self.message_label = customtkinter.CTkLabel(panel, text="", text_color="tomato")
        self.message_label.grid(row=1, column=0, columnspan=3, sticky="w", padx=8)

    def _build_cart_and_history(self) -> None:
        self.cart_panel = customtkinter.CTkScrollableFrame(self, label_text="Itens desta venda")
        self.cart_panel.grid(row=2, column=0, sticky="nsew", padx=(16, 8), pady=(8, 8))
        self.cart_panel.grid_columnconfigure(0, weight=1)
        self.cart_panel.grid_columnconfigure(1, weight=0)

        self.history_panel = customtkinter.CTkScrollableFrame(self, label_text="Histórico de compras do cliente")
        self.history_panel.grid(row=2, column=1, sticky="nsew", padx=(8, 16), pady=(8, 8))
        self.history_panel.grid_columnconfigure(0, weight=1)
        self.history_panel.grid_columnconfigure(1, weight=0)

        bottom_panel = customtkinter.CTkFrame(self, fg_color="transparent")
        bottom_panel.grid(row=3, column=0, columnspan=2, sticky="ew", padx=16, pady=(0, 16))
        bottom_panel.grid_columnconfigure(0, weight=1)

        self.total_label = customtkinter.CTkLabel(bottom_panel, text="Total: R$ 0,00", font=("", 16, "bold"))
        self.total_label.grid(row=0, column=0, sticky="w")

        finalize_button = customtkinter.CTkButton(
            bottom_panel, text="Finalizar venda", command=self._finalize_sale
        )
        finalize_button.grid(row=0, column=1, sticky="e")

    def refresh_customer_and_item_options(self) -> None:
        previously_selected_customer_id = self.customer_id_by_name.get(self.customer_menu.get())
        previously_selected_item_id = self.item_id_by_name.get(self.item_menu.get())

        customers = self.customer_service.list_all_customers()
        self.customer_id_by_name = {customer.full_name: customer.id for customer in customers}
        customer_names = list(self.customer_id_by_name) or [NO_CUSTOMER_SELECTED]
        self.customer_menu.configure(values=customer_names)
        selected_customer_name = self._find_name_by_id(
            self.customer_id_by_name, previously_selected_customer_id, customer_names[0]
        )
        self.customer_menu.set(selected_customer_name)
        self._on_customer_selected(selected_customer_name)

        items = self.stock_item_service.list_all_items()
        self.item_id_by_name = {
            f"{item.name} (estoque: {item.quantity_in_stock})": item.id for item in items
        }
        item_names = list(self.item_id_by_name) or [NO_ITEM_SELECTED]
        self.item_menu.configure(values=item_names)
        selected_item_name = self._find_name_by_id(
            self.item_id_by_name, previously_selected_item_id, item_names[0]
        )
        self.item_menu.set(selected_item_name)

    @staticmethod
    def _find_name_by_id(id_by_name: dict[str, int], target_id: int | None, default_name: str) -> str:
        if target_id is None:
            return default_name
        for name, id_value in id_by_name.items():
            if id_value == target_id:
                return name
        return default_name

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

        stock_item = self.stock_item_service.find_item_by_id(item_id)
        already_in_cart = sum(
            item.desired_quantity for item in self.current_cart_items if item.stock_item_id == item_id
        )
        if stock_item is not None and already_in_cart + quantity > stock_item.quantity_in_stock:
            self.message_label.configure(
                text=(
                    f"Estoque insuficiente para '{stock_item.name}'. "
                    f"Disponível: {stock_item.quantity_in_stock}, já na venda: {already_in_cart}."
                )
            )
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
            text = f"{item_name}  x{item_to_sell.desired_quantity}  =  R$ {subtotal:.2f}"
            customtkinter.CTkLabel(self.cart_panel, text=text, anchor="w").grid(
                row=row_index, column=0, sticky="ew", padx=8, pady=4
            )

            remove_button = customtkinter.CTkButton(
                self.cart_panel, text="Remover", width=80, fg_color="firebrick3", hover_color="firebrick4",
                command=lambda index=row_index: self._remove_item_from_cart(index),
            )
            remove_button.grid(row=row_index, column=1, padx=8, pady=4)

        self.total_label.configure(text=f"Total: R$ {sale_total:.2f}")

    def _remove_item_from_cart(self, index: int) -> None:
        del self.current_cart_items[index]
        self.message_label.configure(text="")
        self._refresh_cart_display()

    def _refresh_selected_customer_history(self) -> None:
        for widget in self.history_panel.winfo_children():
            widget.destroy()

        selected_customer_name = self.customer_menu.get()
        customer_id = self.customer_id_by_name.get(selected_customer_name)
        if customer_id is None:
            return

        previous_sales = self.sale_service.list_purchase_history_by_customer(customer_id)
        if not previous_sales:
            customtkinter.CTkLabel(self.history_panel, text="Nenhuma compra registrada ainda.").grid(
                row=0, column=0, sticky="w", padx=8, pady=8
            )
            return

        for row_index, sale in enumerate(previous_sales):
            self._add_sale_history_row(row_index, sale)

    def _add_sale_history_row(self, row_index: int, sale) -> None:
        formatted_date = sale.sale_date_time.strftime("%d/%m/%Y %H:%M")
        text = (
            f"{formatted_date}  •  {len(sale.sold_items)} item(ns)  •  "
            f"R$ {sale.total_amount:.2f}"
        )
        if sale.is_cancelled:
            text += "  •  (cancelada)"

        label_options = {"text_color": "gray"} if sale.is_cancelled else {}
        label = customtkinter.CTkLabel(self.history_panel, text=text, anchor="w", **label_options)
        label.grid(row=row_index, column=0, sticky="ew", padx=8, pady=4)

        if not sale.is_cancelled:
            cancel_button = customtkinter.CTkButton(
                self.history_panel, text="Cancelar", width=80, fg_color="firebrick3", hover_color="firebrick4",
                command=lambda: self._cancel_sale(sale.id),
            )
            cancel_button.grid(row=row_index, column=1, padx=8, pady=4)

    def _cancel_sale(self, sale_id: int) -> None:
        confirmed = messagebox.askyesno(
            "Cancelar venda", "Tem certeza que deseja cancelar esta venda? Os itens voltam ao estoque."
        )
        if not confirmed:
            return

        try:
            self.sale_service.cancel_sale(sale_id)
        except InvalidSaleDataError as error:
            messagebox.showerror("Não foi possível cancelar", str(error))
            return

        self.refresh_customer_and_item_options()
        self._refresh_selected_customer_history()

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
