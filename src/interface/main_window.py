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

        tab_view = customtkinter.CTkTabview(self)
        tab_view.grid(row=0, column=0, sticky="nsew", padx=12, pady=12)

        tab_view.add(CUSTOMERS_TAB_NAME)
        tab_view.add(STOCK_TAB_NAME)
        tab_view.add(SALES_TAB_NAME)

        customers_screen = CustomersScreen(tab_view.tab(CUSTOMERS_TAB_NAME), customer_service)
        customers_screen.pack(fill="both", expand=True)

        stock_screen = StockScreen(tab_view.tab(STOCK_TAB_NAME), stock_item_service)
        stock_screen.pack(fill="both", expand=True)

        sales_screen = SalesScreen(
            tab_view.tab(SALES_TAB_NAME), customer_service, stock_item_service, sale_service
        )
        sales_screen.pack(fill="both", expand=True)
