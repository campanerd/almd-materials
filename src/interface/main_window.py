import ctypes

import customtkinter

from src.interface import theme
from src.interface.animation import animate, interpolate_color, resolve_color
from src.interface.components import FacetRule
from src.interface.customers_screen import CustomersScreen
from src.interface.sales_screen import SalesScreen
from src.interface.stock_screen import StockScreen
from src.services.customer_service import CustomerService
from src.services.sale_service import SaleService
from src.services.stock_item_service import StockItemService

WINDOW_TITLE = "Almeida - Estoque e Vendas"
WINDOW_SIZE = "1280x760"
MINIMUM_WINDOW_SIZE = (1080, 640)

CUSTOMERS_PAGE = "Clientes"
STOCK_PAGE = "Estoque"
SALES_PAGE = "Vendas"

PAGE_SUBTITLES = {
    CUSTOMERS_PAGE: "Cadastro e histórico de quem compra na loja",
    STOCK_PAGE: "Materiais disponíveis, quantidades e preços",
    SALES_PAGE: "Registro de vendas e histórico do cliente",
}

NAV_INDICATOR_DURATION_MS = 220
DWMWA_USE_IMMERSIVE_DARK_MODE = 20

# Stops CustomTkinter from hiding and re-showing the window on every appearance
# change; the titlebar is themed directly through DWM instead.
customtkinter.CTk._deactivate_windows_window_header_manipulation = True
customtkinter.CTkToplevel._deactivate_windows_window_header_manipulation = True


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
        self.minsize(*MINIMUM_WINDOW_SIZE)
        self.configure(fg_color=theme.BG_CANVAS)

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.navigation_buttons: dict[str, customtkinter.CTkButton] = {}
        self.current_page_name = CUSTOMERS_PAGE

        self._build_sidebar()
        self._build_content_area()
        self._build_pages(customer_service, stock_item_service, sale_service)

        self.after(60, lambda: self._move_navigation_indicator_to(CUSTOMERS_PAGE, animated=False))
        self.after(80, self._apply_titlebar_theme)

    def _build_sidebar(self) -> None:
        sidebar = customtkinter.CTkFrame(
            self, width=theme.SIDEBAR_WIDTH, corner_radius=0, fg_color=theme.BG_SIDEBAR
        )
        sidebar.grid(row=0, column=0, sticky="nsw")
        sidebar.grid_propagate(False)
        sidebar.grid_columnconfigure(0, weight=1)
        sidebar.grid_rowconfigure(2, weight=1)

        brand_block = customtkinter.CTkFrame(sidebar, fg_color="transparent")
        brand_block.grid(row=0, column=0, sticky="ew", padx=22, pady=(26, 30))
        brand_block.grid_columnconfigure(1, weight=1)

        customtkinter.CTkLabel(brand_block, image=theme.logo_image(40), text="").grid(
            row=0, column=0, rowspan=2, sticky="w"
        )
        customtkinter.CTkLabel(
            brand_block,
            text="Almeida",
            font=theme.font("brand"),
            text_color=theme.TEXT_PRIMARY,
            anchor="w",
        ).grid(row=0, column=1, sticky="ew", padx=(12, 0))
        customtkinter.CTkLabel(
            brand_block,
            text="Estoque e Vendas",
            font=theme.font("caption"),
            text_color=theme.TEXT_MUTED,
            anchor="w",
        ).grid(row=1, column=1, sticky="ew", padx=(12, 0))

        navigation_container = customtkinter.CTkFrame(sidebar, fg_color="transparent")
        navigation_container.grid(row=1, column=0, sticky="ew", padx=14)
        navigation_container.grid_columnconfigure(0, weight=1)

        self.navigation_indicator = customtkinter.CTkFrame(
            navigation_container, width=3, height=22, corner_radius=2, fg_color=theme.ACCENT_FG
        )

        for row_index, page_name in enumerate((CUSTOMERS_PAGE, STOCK_PAGE, SALES_PAGE)):
            button = customtkinter.CTkButton(
                navigation_container,
                text=page_name,
                anchor="w",
                height=42,
                corner_radius=10,
                fg_color="transparent",
                hover_color=theme.ROW_HOVER,
                text_color=theme.TEXT_SECONDARY,
                font=theme.font("nav"),
                command=lambda name=page_name: self.show_page(name),
            )
            button.grid(row=row_index, column=0, sticky="ew", pady=3, padx=(10, 0))
            self.navigation_buttons[page_name] = button

        self._build_sidebar_footer(sidebar)

    def _build_sidebar_footer(self, sidebar: customtkinter.CTkFrame) -> None:
        footer = customtkinter.CTkFrame(sidebar, fg_color="transparent")
        footer.grid(row=3, column=0, sticky="ew", padx=24, pady=(0, 24))
        footer.grid_columnconfigure(0, weight=1)

        customtkinter.CTkFrame(footer, height=1, fg_color=theme.DIVIDER).grid(
            row=0, column=0, columnspan=2, sticky="ew", pady=(0, 16)
        )

        customtkinter.CTkLabel(
            footer,
            text="TEMA ESCURO",
            font=theme.font("overline"),
            text_color=theme.TEXT_MUTED,
            anchor="w",
        ).grid(row=1, column=0, sticky="w")

        self.theme_switch = customtkinter.CTkSwitch(
            footer,
            text="",
            width=44,
            command=self._toggle_appearance_mode,
            progress_color=theme.ACCENT_FG,
            fg_color=theme.SWITCH_TRACK,
            button_color=theme.SWITCH_KNOB,
            button_hover_color=theme.SWITCH_KNOB,
        )
        self.theme_switch.grid(row=1, column=1, sticky="e")
        if customtkinter.get_appearance_mode() == "Dark":
            self.theme_switch.select()

    def _build_content_area(self) -> None:
        content = customtkinter.CTkFrame(self, fg_color="transparent")
        content.grid(row=0, column=1, sticky="nsew")
        content.grid_columnconfigure(0, weight=1)
        content.grid_rowconfigure(2, weight=1)

        header = customtkinter.CTkFrame(content, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=34, pady=(30, 16))
        header.grid_columnconfigure(0, weight=1)

        self.page_title_label = customtkinter.CTkLabel(
            header,
            text=CUSTOMERS_PAGE,
            font=theme.font("display"),
            text_color=theme.TEXT_PRIMARY,
            anchor="w",
        )
        self.page_title_label.grid(row=0, column=0, sticky="ew")

        self.page_subtitle_label = customtkinter.CTkLabel(
            header,
            text=PAGE_SUBTITLES[CUSTOMERS_PAGE],
            font=theme.font("caption"),
            text_color=theme.TEXT_MUTED,
            anchor="w",
        )
        self.page_subtitle_label.grid(row=1, column=0, sticky="ew", pady=(2, 0))

        FacetRule(content, height=3).grid(row=1, column=0, sticky="ew", padx=34)

        self.page_container = customtkinter.CTkFrame(content, fg_color="transparent")
        self.page_container.grid(row=2, column=0, sticky="nsew", padx=34, pady=(18, 26))
        self.page_container.grid_columnconfigure(0, weight=1)
        self.page_container.grid_rowconfigure(0, weight=1)

    def _build_pages(
        self,
        customer_service: CustomerService,
        stock_item_service: StockItemService,
        sale_service: SaleService,
    ) -> None:
        self.customers_screen = CustomersScreen(self.page_container, customer_service)
        self.stock_screen = StockScreen(self.page_container, stock_item_service)
        self.sales_screen = SalesScreen(
            self.page_container, customer_service, stock_item_service, sale_service
        )

        self.pages = {
            CUSTOMERS_PAGE: self.customers_screen,
            STOCK_PAGE: self.stock_screen,
            SALES_PAGE: self.sales_screen,
        }
        for page in self.pages.values():
            page.grid(row=0, column=0, sticky="nsew")
            page.grid_remove()

        self.customers_screen.grid()
        self._highlight_navigation_button(CUSTOMERS_PAGE)

    def show_page(self, page_name: str) -> None:
        if page_name == self.current_page_name:
            return

        self.pages[self.current_page_name].grid_remove()
        self.current_page_name = page_name
        self.pages[page_name].grid()

        self.page_title_label.configure(text=page_name)
        self.page_subtitle_label.configure(text=PAGE_SUBTITLES[page_name])
        self._highlight_navigation_button(page_name)
        self._move_navigation_indicator_to(page_name)
        self._refresh_page_data(page_name)

    def _refresh_page_data(self, page_name: str) -> None:
        """Every switch re-reads from the services: a customer registered on one page
        has to appear in the dropdowns of another without restarting the app."""
        if page_name == CUSTOMERS_PAGE:
            self.customers_screen.refresh_customer_list()
        elif page_name == STOCK_PAGE:
            self.stock_screen.refresh_item_list()
        elif page_name == SALES_PAGE:
            self.sales_screen.refresh_customer_and_item_options()

    def _highlight_navigation_button(self, active_page_name: str) -> None:
        for page_name, button in self.navigation_buttons.items():
            is_active = page_name == active_page_name
            button.configure(
                fg_color=theme.NAV_PILL if is_active else "transparent",
                text_color=theme.NAV_PILL_TEXT if is_active else theme.TEXT_SECONDARY,
                font=theme.font("body_strong") if is_active else theme.font("nav"),
            )

    def _move_navigation_indicator_to(self, page_name: str, animated: bool = True) -> None:
        button = self.navigation_buttons[page_name]
        target_y = button.winfo_y() + (button.winfo_height() - 22) // 2

        if not animated:
            self.navigation_indicator.place(x=0, y=target_y)
            return

        start_y = self.navigation_indicator.winfo_y()
        animate(
            self.navigation_indicator,
            NAV_INDICATOR_DURATION_MS,
            lambda progress: self.navigation_indicator.place(
                x=0, y=round(start_y + (target_y - start_y) * progress)
            ),
        )

    def _toggle_appearance_mode(self) -> None:
        customtkinter.set_appearance_mode("dark" if self.theme_switch.get() else "light")
        self._apply_titlebar_theme()
        self._repaint_after_theme_change()

    def _repaint_after_theme_change(self) -> None:
        """Only the visible page is rebuilt: repainting all three at once made the
        switch block for most of a second, and the hidden ones are refreshed anyway
        the moment they are navigated to."""
        self.pages[self.current_page_name].repaint_for_theme_change()

    def _apply_titlebar_theme(self) -> None:
        """CustomTkinter's own titlebar handling hides and re-shows the window, which
        flashes on every theme switch. The flag turns that off and the DWM attribute
        is set directly instead."""
        try:
            window_handle = ctypes.windll.user32.GetParent(self.winfo_id())
            use_dark_titlebar = ctypes.c_int(1 if customtkinter.get_appearance_mode() == "Dark" else 0)
            ctypes.windll.dwmapi.DwmSetWindowAttribute(
                window_handle,
                DWMWA_USE_IMMERSIVE_DARK_MODE,
                ctypes.byref(use_dark_titlebar),
                ctypes.sizeof(use_dark_titlebar),
            )
        except (AttributeError, OSError):
            pass
