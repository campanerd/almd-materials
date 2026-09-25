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
from src.interface.dialogs import ask_confirmation, ask_yes_no, show_error
from src.models.sale import Sale
from src.services.customer_service import CustomerService
from src.services.receipt_service import ReceiptError, ReceiptService
from src.services.sale_service import (
    InsufficientStockError,
    InvalidSaleDataError,
    ItemToSell,
    SaleService,
)
from src.services.stock_item_service import StockItemService

NO_CUSTOMER_SELECTED = "Selecione um cliente"
NO_ITEM_SELECTED = "Selecione um item"
SELECTION_HINT = "Escolha o cliente e o item, informe a quantidade e adicione à venda."

CART_COLUMN_WEIGHTS = [(5, 90), (0, 44), (2, 84), (0, 74)]
CART_COLUMN_TITLES = ["Item", "Qtd.", "Subtotal", ""]

HISTORY_COLUMN_WEIGHTS = [(4, 118), (2, 58), (3, 92), (0, 72)]
HISTORY_COLUMN_TITLES = ["Data", "Itens", "Total", ""]

CELL_PADDING = (0, 8)


def format_amount_in_brazilian_currency(amount: float) -> str:
    """Python groups thousands with the comma and Brazil with the dot, so the two
    separators are swapped through a placeholder that neither of them uses."""
    grouped_amount = f"{amount:,.2f}"
    return "R$ " + grouped_amount.replace(",", "|").replace(".", ",").replace("|", ".")


def _build_section_title(master, text: str) -> customtkinter.CTkLabel:
    return customtkinter.CTkLabel(
        master,
        text=text,
        font=theme.font("section"),
        text_color=theme.TEXT_PRIMARY,
        anchor="w",
    )


def _build_labelled_control_container(master, label_text: str) -> customtkinter.CTkFrame:
    """build_field covers entries only, and the option menus need the same label
    treatment so the whole selection row lines up."""
    container = customtkinter.CTkFrame(master, fg_color="transparent")
    container.grid_columnconfigure(0, weight=1)

    customtkinter.CTkLabel(
        container,
        text=label_text.upper(),
        font=theme.font("overline"),
        text_color=theme.TEXT_MUTED,
        anchor="w",
    ).grid(row=0, column=0, sticky="ew", pady=(0, 5))

    return container


def _build_option_menu(master, values: list[str], command=None) -> customtkinter.CTkOptionMenu:
    return customtkinter.CTkOptionMenu(
        master,
        values=values,
        command=command,
        height=38,
        corner_radius=theme.CONTROL_RADIUS,
        fg_color=theme.ENTRY_FILL,
        button_color=theme.ACCENT,
        button_hover_color=theme.ACCENT_HOVER,
        text_color=theme.TEXT_PRIMARY,
        dropdown_fg_color=theme.BG_ELEVATED,
        dropdown_hover_color=theme.ROW_HOVER,
        dropdown_text_color=theme.TEXT_PRIMARY,
        font=theme.font("body"),
        dropdown_font=theme.font("body"),
        # Otherwise the menu grows to the longest item label and drags the whole
        # selection row wider whenever a long product name is registered.
        dynamic_resizing=False,
    )


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
        self.receipt_service = ReceiptService()

        self.customer_id_by_name: dict[str, int] = {}
        self.item_id_by_name: dict[str, int] = {}
        self.current_cart_items: list[ItemToSell] = []

        self.grid_columnconfigure((0, 1), weight=1, uniform="sales_columns")
        self.grid_rowconfigure(1, weight=1)

        self._build_selection_card()
        self._build_cart_card()
        self._build_history_card()

        self._refresh_cart_display()
        self.refresh_customer_and_item_options()

    def _build_selection_card(self) -> None:
        card = SectionCard(self)
        card.grid(row=0, column=0, columnspan=2, sticky="ew")
        card.grid_columnconfigure((0, 1), weight=1)

        _build_section_title(card, "Nova venda").grid(
            row=0, column=0, columnspan=3, sticky="ew", padx=20, pady=(18, 14)
        )

        customer_container = _build_labelled_control_container(card, "Cliente")
        customer_container.grid(row=1, column=0, sticky="ew", padx=(20, 8))
        self.customer_menu = _build_option_menu(
            customer_container, [NO_CUSTOMER_SELECTED], self._on_customer_selected
        )
        self.customer_menu.grid(row=1, column=0, sticky="ew")

        item_container = _build_labelled_control_container(card, "Item do estoque")
        item_container.grid(row=1, column=1, sticky="ew", padx=8)
        self.item_menu = _build_option_menu(item_container, [NO_ITEM_SELECTED])
        self.item_menu.grid(row=1, column=0, sticky="ew")

        quantity_container, self.quantity_field = build_field(
            card, "Quantidade", "Ex.: 3", width=130
        )
        quantity_container.grid(row=1, column=2, sticky="ew", padx=(8, 20))

        self.message_label = customtkinter.CTkLabel(
            card,
            text=SELECTION_HINT,
            font=theme.font("caption"),
            text_color=theme.TEXT_MUTED,
            anchor="w",
        )
        self.message_label.grid(row=2, column=0, columnspan=2, sticky="ew", padx=20, pady=(14, 18))

        add_button = build_primary_button(card, "Adicionar à venda", self._add_item_to_cart)
        add_button.grid(row=2, column=2, sticky="e", padx=(8, 20), pady=(14, 18))

    def _build_cart_card(self) -> None:
        card = SectionCard(self)
        card.grid(row=1, column=0, sticky="nsew", padx=(0, 9), pady=(18, 0))
        card.grid_columnconfigure(0, weight=1)
        card.grid_rowconfigure(1, weight=1)

        _build_section_title(card, "Itens desta venda").grid(
            row=0, column=0, sticky="ew", padx=20, pady=(18, 10)
        )

        self.cart_list_panel = customtkinter.CTkScrollableFrame(
            card,
            fg_color=theme.BG_CANVAS,
            corner_radius=10,
            scrollbar_button_color=theme.SWITCH_TRACK,
            scrollbar_button_hover_color=theme.ACCENT_FG,
        )
        self.cart_list_panel.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        self.cart_list_panel.grid_columnconfigure(0, weight=1)

        self._build_checkout_bar(card)

    def _build_checkout_bar(self, card: SectionCard) -> None:
        customtkinter.CTkFrame(card, height=1, fg_color=theme.DIVIDER).grid(
            row=2, column=0, sticky="ew", padx=10
        )

        checkout_bar = customtkinter.CTkFrame(
            card, fg_color=theme.BG_ELEVATED, corner_radius=theme.CONTROL_RADIUS
        )
        checkout_bar.grid(row=3, column=0, sticky="ew", padx=10, pady=10)
        checkout_bar.grid_columnconfigure(0, weight=1)

        self.total_label = customtkinter.CTkLabel(
            checkout_bar,
            text=f"Total: {format_amount_in_brazilian_currency(0.0)}",
            font=theme.font("total"),
            text_color=theme.TEXT_PRIMARY,
            anchor="w",
        )
        self.total_label.grid(row=0, column=0, sticky="ew", padx=16, pady=(14, 10))

        finalize_button = build_primary_button(checkout_bar, "Finalizar venda", self._finalize_sale)
        finalize_button.configure(height=44)
        finalize_button.grid(row=1, column=0, sticky="ew", padx=16, pady=(0, 16))

    def _build_history_card(self) -> None:
        card = SectionCard(self)
        card.grid(row=1, column=1, sticky="nsew", padx=(9, 0), pady=(18, 0))
        card.grid_columnconfigure(0, weight=1)
        card.grid_rowconfigure(1, weight=1)

        _build_section_title(card, "Histórico de compras do cliente").grid(
            row=0, column=0, sticky="ew", padx=20, pady=(18, 10)
        )

        self.history_list_panel = customtkinter.CTkScrollableFrame(
            card,
            fg_color=theme.BG_CANVAS,
            corner_radius=10,
            scrollbar_button_color=theme.SWITCH_TRACK,
            scrollbar_button_hover_color=theme.ACCENT_FG,
        )
        self.history_list_panel.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        self.history_list_panel.grid_columnconfigure(0, weight=1)

    def _show_message(self, message: str, is_error: bool) -> None:
        """The strip always carries text so the card never changes height."""
        self.message_label.configure(
            text=message or SELECTION_HINT,
            text_color=theme.DANGER if is_error else theme.TEXT_MUTED,
        )

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
        """The selection is restored by id: the item label carries the live stock, so it
        changes on every sale and a match by label text would silently reset the menu."""
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
            self._show_message("Cadastre ao menos um item em estoque antes de vender.", is_error=True)
            return

        try:
            quantity = int(self.quantity_field.get())
            if quantity <= 0:
                raise ValueError
        except ValueError:
            self._show_message("Informe uma quantidade válida.", is_error=True)
            return

        stock_item = self.stock_item_service.find_item_by_id(item_id)
        # The lines already in the cart count against the stock too, otherwise the same
        # item could be added twice and only fail when the sale is finalized.
        already_in_cart = sum(
            item.desired_quantity for item in self.current_cart_items if item.stock_item_id == item_id
        )
        if stock_item is not None and already_in_cart + quantity > stock_item.quantity_in_stock:
            self._show_message(
                f"Estoque insuficiente para '{stock_item.name}'. "
                f"Disponível: {stock_item.quantity_in_stock}, já na venda: {already_in_cart}.",
                is_error=True,
            )
            return

        self._show_message("", is_error=False)
        self.current_cart_items.append(ItemToSell(stock_item_id=item_id, desired_quantity=quantity))
        self.quantity_field.delete(0, "end")
        self._refresh_cart_display()

    def _refresh_cart_display(self) -> None:
        for widget in self.cart_list_panel.winfo_children():
            widget.destroy()

        if not self.current_cart_items:
            self.total_label.configure(text=f"Total: {format_amount_in_brazilian_currency(0.0)}")
            EmptyState(
                self.cart_list_panel,
                "Nenhum item nesta venda ainda.",
                "Escolha um item acima e informe a quantidade.",
            ).grid(row=0, column=0, sticky="ew")
            return

        build_list_header(self.cart_list_panel, CART_COLUMN_WEIGHTS, CART_COLUMN_TITLES).grid(
            row=0, column=0, sticky="ew", pady=(0, 4)
        )

        item_name_by_id = {item_id: name for name, item_id in self.item_id_by_name.items()}
        stock_items_by_id = {item.id: item for item in self.stock_item_service.list_all_items()}

        sale_total = 0.0
        rows = []
        for row_index, item_to_sell in enumerate(self.current_cart_items):
            stock_item = stock_items_by_id.get(item_to_sell.stock_item_id)
            unit_price = stock_item.unit_price if stock_item else 0.0
            subtotal = unit_price * item_to_sell.desired_quantity
            sale_total += subtotal

            rows.append(
                self._build_cart_row(
                    row_index,
                    item_name_by_id.get(item_to_sell.stock_item_id, "Item"),
                    item_to_sell.desired_quantity,
                    subtotal,
                    # The default argument freezes this line's index at build time: a bare
                    # closure over row_index would make every button remove the last line.
                    lambda index=row_index: self._remove_item_from_cart(index),
                )
            )

        animate_rows_entrance(rows)
        self.total_label.configure(text=f"Total: {format_amount_in_brazilian_currency(sale_total)}")

    def _build_cart_row(
        self, row_index: int, item_name: str, quantity: int, subtotal: float, remove_command
    ) -> DataRow:
        row = DataRow(self.cart_list_panel, CART_COLUMN_WEIGHTS, on_activate=None)
        row.grid(row=row_index + 1, column=0, sticky="ew", pady=2)

        customtkinter.CTkLabel(
            row,
            text=item_name,
            font=theme.font("body_strong"),
            text_color=theme.TEXT_PRIMARY,
            anchor="w",
        ).grid(row=0, column=1, sticky="ew", padx=CELL_PADDING)

        customtkinter.CTkLabel(
            row,
            text=f"x{quantity}",
            font=theme.font("numeric"),
            text_color=theme.TEXT_SECONDARY,
            anchor="w",
        ).grid(row=0, column=2, sticky="ew", padx=CELL_PADDING)

        customtkinter.CTkLabel(
            row,
            text=format_amount_in_brazilian_currency(subtotal),
            font=theme.font("numeric_strong"),
            text_color=theme.TEXT_PRIMARY,
            anchor="w",
        ).grid(row=0, column=3, sticky="ew", padx=CELL_PADDING)

        build_danger_button(row, "Remover", remove_command, width=74).grid(
            row=0, column=4, padx=CELL_PADDING
        )

        row.finish_setup()
        return row

    def _remove_item_from_cart(self, index: int) -> None:
        del self.current_cart_items[index]
        self._show_message("", is_error=False)
        self._refresh_cart_display()

    def _refresh_selected_customer_history(self) -> None:
        for widget in self.history_list_panel.winfo_children():
            widget.destroy()

        selected_customer_name = self.customer_menu.get()
        customer_id = self.customer_id_by_name.get(selected_customer_name)
        if customer_id is None:
            EmptyState(
                self.history_list_panel,
                "Nenhum cliente selecionado.",
                "Cadastre um cliente para registrar uma venda.",
            ).grid(row=0, column=0, sticky="ew")
            return

        previous_sales = self.sale_service.list_purchase_history_by_customer(customer_id)
        if not previous_sales:
            EmptyState(
                self.history_list_panel,
                "Nenhuma compra registrada ainda.",
                "As vendas finalizadas para este cliente aparecem aqui.",
            ).grid(row=0, column=0, sticky="ew")
            return

        build_list_header(self.history_list_panel, HISTORY_COLUMN_WEIGHTS, HISTORY_COLUMN_TITLES).grid(
            row=0, column=0, sticky="ew", pady=(0, 4)
        )

        rows = [
            self._build_sale_history_row(row_index, sale)
            for row_index, sale in enumerate(previous_sales)
        ]
        animate_rows_entrance(rows)

    def _build_sale_history_row(self, row_index: int, sale: Sale) -> DataRow:
        row = DataRow(self.history_list_panel, HISTORY_COLUMN_WEIGHTS, on_activate=None)
        row.grid(row=row_index + 1, column=0, sticky="ew", pady=2)

        date_text_color = theme.TEXT_MUTED if sale.is_cancelled else theme.TEXT_PRIMARY
        detail_text_color = theme.TEXT_MUTED if sale.is_cancelled else theme.TEXT_SECONDARY

        customtkinter.CTkLabel(
            row,
            text=sale.sale_date_time.strftime("%d/%m/%Y %H:%M"),
            font=theme.font("numeric"),
            text_color=date_text_color,
            anchor="w",
        ).grid(row=0, column=1, sticky="ew", padx=CELL_PADDING)

        customtkinter.CTkLabel(
            row,
            text=f"{len(sale.sold_items)} item(ns)",
            font=theme.font("body"),
            text_color=detail_text_color,
            anchor="w",
        ).grid(row=0, column=2, sticky="ew", padx=CELL_PADDING)

        customtkinter.CTkLabel(
            row,
            text=format_amount_in_brazilian_currency(sale.total_amount),
            font=theme.font("numeric_strong"),
            text_color=date_text_color,
            anchor="w",
        ).grid(row=0, column=3, sticky="ew", padx=CELL_PADDING)

        if sale.is_cancelled:
            customtkinter.CTkLabel(
                row,
                text="(cancelada)",
                font=theme.font("caption"),
                text_color=theme.TEXT_MUTED,
                anchor="w",
            ).grid(row=0, column=4, sticky="ew", padx=CELL_PADDING)
        else:
            build_danger_button(
                row, "Cancelar", lambda: self._cancel_sale(sale.id), width=72
            ).grid(row=0, column=4, padx=CELL_PADDING)

        row.finish_setup()
        return row

    def _cancel_sale(self, sale_id: int) -> None:
        confirmed = ask_confirmation(
            self.winfo_toplevel(),
            "Cancelar venda",
            "Tem certeza que deseja cancelar esta venda? Os itens voltam ao estoque.",
            "Cancelar venda",
        )
        if not confirmed:
            return

        try:
            self.sale_service.cancel_sale(sale_id)
        except InvalidSaleDataError as error:
            show_error(self.winfo_toplevel(), "Não foi possível cancelar", str(error))
            return

        self.refresh_customer_and_item_options()
        self._refresh_selected_customer_history()

    def _finalize_sale(self) -> None:
        selected_customer_name = self.customer_menu.get()
        customer_id = self.customer_id_by_name.get(selected_customer_name)

        if customer_id is None:
            self._show_message("Cadastre ao menos um cliente antes de vender.", is_error=True)
            return
        if not self.current_cart_items:
            self._show_message("Adicione ao menos um item à venda.", is_error=True)
            return

        should_send_receipt = ask_yes_no(
            self.winfo_toplevel(),
            "Finalizar venda",
            "Deseja enviar o recibo?",
        )

        customer = self.customer_service.find_customer_by_id(customer_id)
        item_name_by_id = {
            item.id: item.name for item in self.stock_item_service.list_all_items() if item.id is not None
        }

        try:
            sale = self.sale_service.register_sale(customer_id, self.current_cart_items)
        except (InvalidSaleDataError, InsufficientStockError) as error:
            self._show_message(str(error), is_error=True)
            return

        receipt_path = None
        if should_send_receipt and customer is not None:
            try:
                receipt_path = self.receipt_service.generate_pdf(sale, customer, item_name_by_id)
                self.receipt_service.open_whatsapp(customer)
            except ReceiptError as error:
                show_error(
                    self.winfo_toplevel(),
                    "Venda finalizada",
                    f"A venda foi concluída, mas o envio do recibo não pôde ser preparado.\n\n{error}",
                )

        self.current_cart_items = []
        self._refresh_cart_display()
        self.refresh_customer_and_item_options()
        self._refresh_selected_customer_history()

        if receipt_path is not None:
            self._show_message(
                f"Venda finalizada. Recibo salvo em: {receipt_path}",
                is_error=False,
            )
        else:
            self._show_message("Venda finalizada com sucesso.", is_error=False)

    def repaint_for_theme_change(self) -> None:
        """Hover tweens leave literal colors on the rows, which would freeze across an
        appearance change, so both lists are rebuilt from the current tokens."""
        self._refresh_cart_display()
        self._refresh_selected_customer_history()
