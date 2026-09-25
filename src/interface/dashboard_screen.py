import customtkinter

from src.interface import theme
from src.interface.components import SectionCard


MONTHLY_SALES = [
    ("Jan", 11200),
    ("Fev", 13850),
    ("Mar", 12600),
    ("Abr", 15400),
    ("Mai", 14950),
    ("Jun", 17300),
    ("Jul", 18900),
    ("Ago", 22900),
    ("Set", 19600),
    ("Out", 16500),
    ("Nov", 12420),
    ("Dez", 10800),
]

LOW_STOCK_ITEMS = [
    ("Tinta branca premium", "3 un."),
    ("Argamassa AC-II", "5 un."),
    ("Rejunte cinza", "7 un."),
    ("Cimento CP-II", "8 un."),
]

TOP_CATEGORIES = [
    ("Material básico", 0.42, "42%"),
    ("Acabamento", 0.31, "31%"),
    ("Hidráulica", 0.17, "17%"),
    ("Elétrica", 0.10, "10%"),
]

RECENT_SALES = [
    ("Davi Almeida", "Hoje, 09:42", "R$ 1.284,90"),
    ("Mariana Souza", "Ontem, 16:18", "R$ 742,50"),
    ("Construtora Lima", "Ontem, 11:06", "R$ 2.930,00"),
]


class DashboardScreen(customtkinter.CTkFrame):
    """Presentation-first dashboard using intentionally mocked data.

    The prototype has no dependency on repositories/services yet. That keeps the
    dashboard visually demonstrable while the final business metrics are still being
    defined.
    """

    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.body = customtkinter.CTkScrollableFrame(
            self,
            fg_color="transparent",
            corner_radius=0,
            scrollbar_button_color=theme.SWITCH_TRACK,
            scrollbar_button_hover_color=theme.ACCENT_FG,
        )
        self.body.grid(row=0, column=0, sticky="nsew")
        self.body.grid_columnconfigure(0, weight=1)

        self._build_metric_cards()
        self._build_main_row()
        self._build_bottom_row()

    def _build_metric_cards(self) -> None:
        row = customtkinter.CTkFrame(self.body, fg_color="transparent")
        row.grid(row=0, column=0, sticky="ew", pady=(0, 16))
        for column in range(4):
            row.grid_columnconfigure(column, weight=1, uniform="dashboard-metrics")

        metrics = (
            ("Faturamento no ano", "R$ 186.420", "+12,8%", "vs. ano anterior"),
            ("Vendas realizadas", "428", "+34", "neste ano"),
            ("Ticket médio", "R$ 435,56", "+6,4%", "por venda"),
            ("Clientes atendidos", "173", "+21", "novos clientes"),
        )

        for column, metric in enumerate(metrics):
            self._metric_card(row, *metric).grid(
                row=0,
                column=column,
                sticky="nsew",
                padx=(0 if column == 0 else 6, 0 if column == 3 else 6),
            )

    def _metric_card(self, master, label: str, value: str, trend: str, caption: str):
        card = SectionCard(master)
        card.grid_columnconfigure(0, weight=1)

        customtkinter.CTkFrame(
            card,
            width=4,
            height=44,
            corner_radius=2,
            fg_color=theme.ACCENT_FG,
        ).grid(row=0, column=0, rowspan=2, sticky="w", padx=(16, 0), pady=(18, 0))

        customtkinter.CTkLabel(
            card,
            text=label.upper(),
            font=theme.font("overline"),
            text_color=theme.TEXT_MUTED,
            anchor="w",
        ).grid(row=0, column=0, sticky="ew", padx=(30, 16), pady=(16, 2))

        customtkinter.CTkLabel(
            card,
            text=value,
            font=theme.font("title"),
            text_color=theme.TEXT_PRIMARY,
            anchor="w",
        ).grid(row=1, column=0, sticky="ew", padx=(30, 16))

        footer = customtkinter.CTkFrame(card, fg_color="transparent")
        footer.grid(row=2, column=0, sticky="ew", padx=16, pady=(10, 14))
        customtkinter.CTkLabel(
            footer,
            text=trend,
            font=theme.font("caption"),
            text_color=theme.SUCCESS,
        ).pack(side="left")
        customtkinter.CTkLabel(
            footer,
            text=f"  {caption}",
            font=theme.font("caption"),
            text_color=theme.TEXT_MUTED,
        ).pack(side="left")

        return card

    def _build_main_row(self) -> None:
        row = customtkinter.CTkFrame(self.body, fg_color="transparent")
        row.grid(row=1, column=0, sticky="nsew")
        row.grid_columnconfigure(0, weight=2, uniform="dashboard-main")
        row.grid_columnconfigure(1, weight=1, uniform="dashboard-main")

        self._build_sales_chart(row).grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        self._build_low_stock_card(row).grid(row=0, column=1, sticky="nsew", padx=(8, 0))

    def _build_sales_chart(self, master):
        card = SectionCard(master)
        card.grid_columnconfigure(0, weight=1)

        header = customtkinter.CTkFrame(card, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=20, pady=(18, 8))
        header.grid_columnconfigure(0, weight=1)

        customtkinter.CTkLabel(
            header,
            text="Vendas ao longo do ano",
            font=theme.font("section"),
            text_color=theme.TEXT_PRIMARY,
            anchor="w",
        ).grid(row=0, column=0, sticky="w")
        customtkinter.CTkLabel(
            header,
            text="DADOS DEMONSTRATIVOS",
            font=theme.font("overline"),
            text_color=theme.BRAND_MID,
        ).grid(row=0, column=1, sticky="e")
        customtkinter.CTkLabel(
            header,
            text="Faturamento mensal em reais",
            font=theme.font("caption"),
            text_color=theme.TEXT_MUTED,
            anchor="w",
        ).grid(row=1, column=0, columnspan=2, sticky="w", pady=(3, 0))

        plot = customtkinter.CTkFrame(card, fg_color="transparent", height=214)
        plot.grid(row=1, column=0, sticky="ew", padx=20, pady=(4, 18))
        plot.grid_propagate(False)
        plot.grid_rowconfigure(0, weight=1)
        for column in range(len(MONTHLY_SALES)):
            plot.grid_columnconfigure(column, weight=1, uniform="month")

        max_value = max(value for _, value in MONTHLY_SALES)
        for column, (month, value) in enumerate(MONTHLY_SALES):
            bar_column = customtkinter.CTkFrame(plot, fg_color="transparent")
            bar_column.grid(row=0, column=column, sticky="nsew", padx=3)
            bar_column.grid_rowconfigure(0, weight=1)
            bar_column.grid_columnconfigure(0, weight=1)

            bar_area = customtkinter.CTkFrame(bar_column, fg_color="transparent", height=166)
            bar_area.grid(row=0, column=0, sticky="nsew")
            bar_area.grid_propagate(False)
            bar_area.grid_columnconfigure(0, weight=1)
            bar_area.grid_rowconfigure(0, weight=1)

            height = max(24, int(142 * (value / max_value)))
            bar = customtkinter.CTkFrame(
                bar_area,
                height=height,
                corner_radius=6,
                fg_color=theme.ACCENT_FG if value == max_value else theme.BRAND_SAGE,
            )
            bar.grid(row=0, column=0, sticky="s", padx=4)
            bar.grid_propagate(False)

            customtkinter.CTkLabel(
                bar_column,
                text=month,
                font=theme.font("caption"),
                text_color=theme.TEXT_MUTED,
            ).grid(row=1, column=0, pady=(8, 0))

        return card

    def _build_low_stock_card(self, master):
        card = SectionCard(master)
        card.grid_columnconfigure(0, weight=1)

        customtkinter.CTkLabel(
            card,
            text="Estoque em atenção",
            font=theme.font("section"),
            text_color=theme.TEXT_PRIMARY,
            anchor="w",
        ).grid(row=0, column=0, sticky="ew", padx=20, pady=(18, 2))
        customtkinter.CTkLabel(
            card,
            text="Itens próximos de esgotar",
            font=theme.font("caption"),
            text_color=theme.TEXT_MUTED,
            anchor="w",
        ).grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 10))

        list_frame = customtkinter.CTkFrame(card, fg_color="transparent")
        list_frame.grid(row=2, column=0, sticky="nsew", padx=14, pady=(0, 10))
        list_frame.grid_columnconfigure(0, weight=1)

        for row_index, (name, quantity) in enumerate(LOW_STOCK_ITEMS):
            item = customtkinter.CTkFrame(
                list_frame,
                fg_color=theme.ROW_HOVER,
                corner_radius=10,
                height=48,
            )
            item.grid(row=row_index, column=0, sticky="ew", pady=4)
            item.grid_propagate(False)
            item.grid_columnconfigure(0, weight=1)

            customtkinter.CTkLabel(
                item,
                text=name,
                font=theme.font("body_strong"),
                text_color=theme.TEXT_PRIMARY,
                anchor="w",
            ).grid(row=0, column=0, sticky="ew", padx=(12, 8), pady=10)
            customtkinter.CTkLabel(
                item,
                text=quantity,
                font=theme.font("numeric_strong"),
                text_color=theme.TEXT_PRIMARY,
            ).grid(row=0, column=1, padx=(4, 12), pady=10)

        return card

    def _build_bottom_row(self) -> None:
        row = customtkinter.CTkFrame(self.body, fg_color="transparent")
        row.grid(row=2, column=0, sticky="ew", pady=(16, 2))
        row.grid_columnconfigure(0, weight=1, uniform="dashboard-bottom")
        row.grid_columnconfigure(1, weight=1, uniform="dashboard-bottom")

        self._build_category_card(row).grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        self._build_recent_sales_card(row).grid(row=0, column=1, sticky="nsew", padx=(8, 0))

    def _build_category_card(self, master):
        card = SectionCard(master)
        card.grid_columnconfigure(0, weight=1)

        customtkinter.CTkLabel(
            card,
            text="Categorias mais vendidas",
            font=theme.font("section"),
            text_color=theme.TEXT_PRIMARY,
            anchor="w",
        ).grid(row=0, column=0, sticky="ew", padx=20, pady=(18, 3))
        customtkinter.CTkLabel(
            card,
            text="Participação estimada no faturamento",
            font=theme.font("caption"),
            text_color=theme.TEXT_MUTED,
            anchor="w",
        ).grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 12))

        content = customtkinter.CTkFrame(card, fg_color="transparent")
        content.grid(row=2, column=0, sticky="ew", padx=20, pady=(0, 16))
        content.grid_columnconfigure(0, weight=1)

        for row_index, (name, progress, value) in enumerate(TOP_CATEGORIES):
            line = customtkinter.CTkFrame(content, fg_color="transparent")
            line.grid(row=row_index, column=0, sticky="ew", pady=4)
            line.grid_columnconfigure(0, weight=1)

            customtkinter.CTkLabel(
                line,
                text=name,
                font=theme.font("caption"),
                text_color=theme.TEXT_SECONDARY,
                anchor="w",
            ).grid(row=0, column=0, sticky="w")
            customtkinter.CTkLabel(
                line,
                text=value,
                font=theme.font("numeric"),
                text_color=theme.TEXT_PRIMARY,
            ).grid(row=0, column=1, sticky="e")

            meter = customtkinter.CTkProgressBar(
                line,
                height=7,
                corner_radius=4,
                fg_color=theme.METER_TRACK,
                progress_color=theme.ACCENT_FG,
            )
            meter.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(4, 0))
            meter.set(progress)

        return card

    def _build_recent_sales_card(self, master):
        card = SectionCard(master)
        card.grid_columnconfigure(0, weight=1)

        customtkinter.CTkLabel(
            card,
            text="Últimas vendas",
            font=theme.font("section"),
            text_color=theme.TEXT_PRIMARY,
            anchor="w",
        ).grid(row=0, column=0, sticky="ew", padx=20, pady=(18, 3))
        customtkinter.CTkLabel(
            card,
            text="Movimentações recentes da loja",
            font=theme.font("caption"),
            text_color=theme.TEXT_MUTED,
            anchor="w",
        ).grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 8))

        list_frame = customtkinter.CTkFrame(card, fg_color="transparent")
        list_frame.grid(row=2, column=0, sticky="ew", padx=14, pady=(0, 12))
        list_frame.grid_columnconfigure(0, weight=1)

        for row_index, (customer, when, total) in enumerate(RECENT_SALES):
            item = customtkinter.CTkFrame(list_frame, fg_color="transparent")
            item.grid(row=row_index, column=0, sticky="ew", padx=6, pady=5)
            item.grid_columnconfigure(0, weight=1)

            customtkinter.CTkLabel(
                item,
                text=customer,
                font=theme.font("body_strong"),
                text_color=theme.TEXT_PRIMARY,
                anchor="w",
            ).grid(row=0, column=0, sticky="ew")
            customtkinter.CTkLabel(
                item,
                text=when,
                font=theme.font("caption"),
                text_color=theme.TEXT_MUTED,
                anchor="w",
            ).grid(row=1, column=0, sticky="ew")
            customtkinter.CTkLabel(
                item,
                text=total,
                font=theme.font("numeric_strong"),
                text_color=theme.ACCENT,
            ).grid(row=0, column=1, rowspan=2, sticky="e")

            if row_index < len(RECENT_SALES) - 1:
                customtkinter.CTkFrame(item, height=1, fg_color=theme.DIVIDER).grid(
                    row=2, column=0, columnspan=2, sticky="ew", pady=(8, 0)
                )

        return card

    def repaint_for_theme_change(self) -> None:
        # Every widget uses theme tuples, so CustomTkinter repaints it automatically.
        pass
