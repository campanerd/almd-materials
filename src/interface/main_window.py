import customtkinter

from src.interface.customers_screen import CustomersScreen
from src.interface.sales_screen import SalesScreen
from src.interface.stock_screen import StockScreen
from src.services.customer_service import CustomerService
from src.services.sale_service import SaleService
from src.services.stock_item_service import StockItemService

WINDOW_TITLE = "Almoxarifado - Estoque e Vendas"
WINDOW_SIZE = "1100x650"

CUSTOMERS_TAB_NAME = "Clientes"
STOCK_TAB_NAME = "Estoque"
SALES_TAB_NAME = "Vendas"


class MainWindow(customtkinter.CTk):
    def __init__(
        self,
        customer_service: CustomerService,
        stock_item_service: StockItemService,
        sale_service: SaleService,
    ):
        super().__init__()
        self.title(WINDOW_TITLE)
        self.geometry(WINDOW_SIZE)

        customtkinter.set_appearance_mode("system")
        customtkinter.set_default_color_theme("blue")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.tab_view = customtkinter.CTkTabview(self, command=self._on_tab_changed)
        self.tab_view.grid(row=0, column=0, sticky="nsew", padx=12, pady=12)

        self.tab_view.add(CUSTOMERS_TAB_NAME)
        self.tab_view.add(STOCK_TAB_NAME)
        self.tab_view.add(SALES_TAB_NAME)

        self.customers_screen = CustomersScreen(self.tab_view.tab(CUSTOMERS_TAB_NAME), customer_service)
        self.customers_screen.pack(fill="both", expand=True)

        self.stock_screen = StockScreen(self.tab_view.tab(STOCK_TAB_NAME), stock_item_service)
        self.stock_screen.pack(fill="both", expand=True)

        self.sales_screen = SalesScreen(
            self.tab_view.tab(SALES_TAB_NAME), customer_service, stock_item_service, sale_service
        )
        self.sales_screen.pack(fill="both", expand=True)

    def _on_tab_changed(self) -> None:
        selected_tab_name = self.tab_view.get()

        if selected_tab_name == CUSTOMERS_TAB_NAME:
            self.customers_screen.refresh_customer_list()
        elif selected_tab_name == STOCK_TAB_NAME:
            self.stock_screen.refresh_item_list()
        elif selected_tab_name == SALES_TAB_NAME:
            self.sales_screen.refresh_customer_and_item_options()
