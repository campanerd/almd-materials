import customtkinter

from src.interface.customers_screen import CustomersScreen
from src.interface.sales_screen import SalesScreen
from src.interface.stock_screen import StockScreen
from src.services.customer_service import CustomerService
from src.services.sale_service import SaleService
from src.services.stock_item_service import StockItemService

WINDOW_TITLE = "Almoxarifado - Estoque e Vendas"
WINDOW_SIZE = "1220x760"
MIN_WINDOW_SIZE = (1020, 660)

CUSTOMERS_TAB_NAME = "Clientes"
STOCK_TAB_NAME = "Estoque"
SALES_TAB_NAME = "Vendas"

BACKGROUND = "#F4F8F5"
SURFACE = "#FFFFFF"
PRIMARY_GREEN = "#176B45"
PRIMARY_GREEN_HOVER = "#12583A"
SOFT_GREEN = "#E8F3EC"
SOFT_GREEN_HOVER = "#D9EADD"
BORDER = "#D9E5DE"
TEXT = "#17352A"


class MainWindow(customtkinter.CTk):
    def __init__(
        self,
        customer_service: CustomerService,
        stock_item_service: StockItemService,
        sale_service: SaleService,
    ):
        super().__init__()

        customtkinter.set_appearance_mode("light")

        self.title(WINDOW_TITLE)
        self.geometry(WINDOW_SIZE)
        self.minsize(*MIN_WINDOW_SIZE)
        self.configure(fg_color=BACKGROUND)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        tab_view = customtkinter.CTkTabview(
            self,
            corner_radius=20,
            border_width=1,
            border_color=BORDER,
            fg_color=SURFACE,
            segmented_button_fg_color="#F0F6F2",
            segmented_button_selected_color=PRIMARY_GREEN,
            segmented_button_selected_hover_color=PRIMARY_GREEN_HOVER,
            segmented_button_unselected_color="#F0F6F2",
            segmented_button_unselected_hover_color=SOFT_GREEN_HOVER,
            text_color=TEXT,
        )
        tab_view.grid(row=0, column=0, sticky="nsew", padx=28, pady=28)

        tab_view.add(CUSTOMERS_TAB_NAME)
        tab_view.add(STOCK_TAB_NAME)
        tab_view.add(SALES_TAB_NAME)

        tab_view._segmented_button.configure(
            font=customtkinter.CTkFont(family="Segoe UI", size=14, weight="bold"),
            height=50,
            corner_radius=14,
            border_width=0,
            dynamic_resizing=False,
            width=450,
        )

        for tab_name in (CUSTOMERS_TAB_NAME, STOCK_TAB_NAME, SALES_TAB_NAME):
            tab_view.tab(tab_name).configure(fg_color=SURFACE)

        customers_screen = CustomersScreen(tab_view.tab(CUSTOMERS_TAB_NAME), customer_service)
        customers_screen.pack(fill="both", expand=True)

        stock_screen = StockScreen(tab_view.tab(STOCK_TAB_NAME), stock_item_service)
        stock_screen.pack(fill="both", expand=True)

        sales_screen = SalesScreen(
            tab_view.tab(SALES_TAB_NAME), customer_service, stock_item_service, sale_service
        )
        sales_screen.pack(fill="both", expand=True)
import customtkinter

from src.interface.customers_screen import CustomersScreen
from src.interface.sales_screen import SalesScreen
from src.interface.stock_screen import StockScreen
from src.services.customer_service import CustomerService
from src.services.sale_service import SaleService
from src.services.stock_item_service import StockItemService

WINDOW_TITLE = "Almoxarifado - Estoque e Vendas"
WINDOW_SIZE = "1220x760"
MIN_WINDOW_SIZE = (1020, 660)

CUSTOMERS_TAB_NAME = "Clientes"
STOCK_TAB_NAME = "Estoque"
SALES_TAB_NAME = "Vendas"

BACKGROUND = "#F4F8F5"
SURFACE = "#FFFFFF"
PRIMARY_GREEN = "#176B45"
PRIMARY_GREEN_HOVER = "#12583A"
SOFT_GREEN = "#E8F3EC"
SOFT_GREEN_HOVER = "#D9EADD"
BORDER = "#D9E5DE"
TEXT = "#17352A"


class MainWindow(customtkinter.CTk):
    def __init__(
        self,
        customer_service: CustomerService,
        stock_item_service: StockItemService,
        sale_service: SaleService,
    ):
        super().__init__()

        customtkinter.set_appearance_mode("light")

        self.title(WINDOW_TITLE)
        self.geometry(WINDOW_SIZE)
        self.minsize(*MIN_WINDOW_SIZE)
        self.configure(fg_color=BACKGROUND)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        tab_view = customtkinter.CTkTabview(
            self,
            corner_radius=20,
            border_width=1,
            border_color=BORDER,
            fg_color=SURFACE,
            segmented_button_fg_color="#F0F6F2",
            segmented_button_selected_color=PRIMARY_GREEN,
            segmented_button_selected_hover_color=PRIMARY_GREEN_HOVER,
            segmented_button_unselected_color="#F0F6F2",
            segmented_button_unselected_hover_color=SOFT_GREEN_HOVER,
            text_color=TEXT,
        )
        tab_view.grid(row=0, column=0, sticky="nsew", padx=28, pady=28)

        tab_view.add(CUSTOMERS_TAB_NAME)
        tab_view.add(STOCK_TAB_NAME)
        tab_view.add(SALES_TAB_NAME)

        tab_view._segmented_button.configure(
            font=customtkinter.CTkFont(family="Segoe UI", size=14, weight="bold"),
            height=50,
            corner_radius=14,
            border_width=0,
            dynamic_resizing=False,
            width=450,
        )

        def update_tab_text_colors():
            selected_tab = tab_view.get()

            for tab_name, button in tab_view._segmented_button._buttons_dict.items():
                button.configure(
                    text_color="#FFFFFF" if tab_name == selected_tab else TEXT
                )

        tab_view.configure(command=update_tab_text_colors)
        update_tab_text_colors()

        for tab_name in (CUSTOMERS_TAB_NAME, STOCK_TAB_NAME, SALES_TAB_NAME):
            tab_view.tab(tab_name).configure(fg_color=SURFACE)

        customers_screen = CustomersScreen(tab_view.tab(CUSTOMERS_TAB_NAME), customer_service)
        customers_screen.pack(fill="both", expand=True)

        stock_screen = StockScreen(tab_view.tab(STOCK_TAB_NAME), stock_item_service)
        stock_screen.pack(fill="both", expand=True)

        sales_screen = SalesScreen(
            tab_view.tab(SALES_TAB_NAME), customer_service, stock_item_service, sale_service
        )
        sales_screen.pack(fill="both", expand=True)
