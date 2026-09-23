import customtkinter

from src.interface import theme
from src.interface.animation import (
    animate,
    bind_including_children,
    interpolate_color,
    pointer_is_inside,
    resolve_color,
)

HOVER_DURATION_MS = 130
ROW_ENTRANCE_DURATION_MS = 260
ROW_ENTRANCE_STAGGER_MS = 28
MAX_ANIMATED_ROWS = 14


class FacetRule(customtkinter.CTkFrame):
    """The brand signature: the logo's three greens in the proportion they occupy in
    the mark. It is the one piece of pure decoration in the interface."""

    def __init__(self, master, height: int = 3):
        super().__init__(master, height=height, fg_color="transparent")
        self.grid_propagate(False)
        self.grid_rowconfigure(0, weight=1)

        for column, (weight, color) in enumerate(
            ((3, theme.BRAND_DEEP), (2, theme.BRAND_MID), (5, theme.BRAND_SAGE))
        ):
            self.grid_columnconfigure(column, weight=weight)
            customtkinter.CTkFrame(self, fg_color=color, corner_radius=0).grid(
                row=0, column=column, sticky="nsew"
            )


class SectionCard(customtkinter.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(
            master,
            fg_color=theme.BG_CARD,
            border_width=1,
            border_color=theme.BORDER,
            corner_radius=theme.CARD_RADIUS,
            **kwargs,
        )


def build_column_layout(widget, column_weights: list[tuple[int, int]]) -> None:
    """Applied identically to the header strip and to every row, so the two line up
    by construction at any DPI instead of by hand-tuned padding.

    The uniform group is what makes it exact: without it each grid sizes its columns
    to its own content, so a wide cell pushes the row's columns out of step with the
    narrower header above it.
    """
    for column, (weight, minimum_width) in enumerate(column_weights):
        widget.grid_columnconfigure(
            column + 1,
            weight=weight,
            minsize=minimum_width,
            uniform="datacolumn" if weight else "",
        )


def build_list_header(master, column_weights: list[tuple[int, int]], titles: list[str]):
    """Lives inside the scrollable list and uses the same column layout and padding as
    the rows, so header and data align by construction instead of by tuning."""
    header = customtkinter.CTkFrame(master, fg_color="transparent", height=26)
    header.grid_propagate(False)
    header.grid_rowconfigure(0, weight=1)
    build_column_layout(header, column_weights)

    customtkinter.CTkFrame(
        header, width=theme.ROW_SPINE_WIDTH, height=1, fg_color="transparent"
    ).grid(row=0, column=0, padx=(6, 8))
    for index, title in enumerate(titles):
        customtkinter.CTkLabel(
            header,
            text=title.upper(),
            font=theme.font("overline"),
            text_color=theme.TEXT_MUTED,
            anchor="w",
        ).grid(row=0, column=index + 1, sticky="ew", padx=(0, 12))

    return header


class DataRow(customtkinter.CTkFrame):
    """A list row that behaves like an object: it lights up under the pointer and
    opens its editor on a double click, with no button to hunt for."""

    def __init__(self, master, column_weights: list[tuple[int, int]], on_activate=None):
        super().__init__(
            master,
            height=theme.ROW_HEIGHT,
            fg_color=theme.BG_CARD,
            corner_radius=10,
        )
        self.grid_propagate(False)
        self.grid_rowconfigure(0, weight=1)
        build_column_layout(self, column_weights)

        self.accent_spine = customtkinter.CTkFrame(
            self, width=theme.ROW_SPINE_WIDTH, fg_color=theme.BG_CARD, corner_radius=2
        )
        self.accent_spine.grid(row=0, column=0, sticky="ns", padx=(6, 8), pady=10)

        self._on_activate = on_activate
        self._hover_progress = 0.0

    def finish_setup(self) -> None:
        """Called once the row's children exist, since the pointer and double-click
        bindings have to reach them too."""
        bind_including_children(self, "<Enter>", self._handle_pointer_enter)
        bind_including_children(self, "<Leave>", self._handle_pointer_leave)
        if self._on_activate is not None:
            bind_including_children(self, "<Double-Button-1>", self._handle_activate)

    def _handle_activate(self, _event=None) -> None:
        self._on_activate()

    def _handle_pointer_enter(self, _event=None) -> None:
        self._animate_hover_to(1.0)

    def _handle_pointer_leave(self, _event=None) -> None:
        if pointer_is_inside(self):
            return
        self._animate_hover_to(0.0)

    def _animate_hover_to(self, target: float) -> None:
        start = self._hover_progress
        if start == target:
            return

        resting_background = resolve_color(theme.BG_CARD)
        hovered_background = resolve_color(theme.ROW_HOVER)
        spine_color = resolve_color(theme.ACCENT_FG)

        def apply(progress: float) -> None:
            current = start + (target - start) * progress
            self._hover_progress = current
            self.configure(fg_color=interpolate_color(resting_background, hovered_background, current))
            self.accent_spine.configure(
                fg_color=interpolate_color(resting_background, spine_color, current)
            )

        animate(self, HOVER_DURATION_MS, apply)


def animate_rows_entrance(rows: list[DataRow]) -> None:
    """Rows wash in one after another. The cascade is a color ramp rather than a
    geometry tween: moving gridded rows reflows the whole list every frame, and only
    a short stagger window keeps the frame budget intact on a long list."""
    canvas_color = resolve_color(theme.BG_CANVAS)
    card_color = resolve_color(theme.BG_CARD)

    for index, row in enumerate(rows[:MAX_ANIMATED_ROWS]):
        row.configure(fg_color=canvas_color)
        _schedule_row_entrance(row, index, canvas_color, card_color)


def _schedule_row_entrance(row: DataRow, index: int, from_color: str, to_color: str) -> None:
    def start() -> None:
        if not row.winfo_exists():
            return
        animate(
            row,
            ROW_ENTRANCE_DURATION_MS,
            lambda progress: row.configure(
                fg_color=interpolate_color(from_color, to_color, progress)
            ),
        )

    row.after(index * ROW_ENTRANCE_STAGGER_MS, start)


class EmptyState(customtkinter.CTkFrame):
    def __init__(self, master, message: str, hint: str):
        super().__init__(master, fg_color="transparent")
        self.grid_columnconfigure(0, weight=1)

        customtkinter.CTkLabel(self, image=theme.logo_image(52), text="").grid(
            row=0, column=0, pady=(26, 12)
        )
        customtkinter.CTkLabel(
            self, text=message, font=theme.font("body_strong"), text_color=theme.TEXT_SECONDARY
        ).grid(row=1, column=0)
        customtkinter.CTkLabel(
            self, text=hint, font=theme.font("caption"), text_color=theme.TEXT_MUTED, wraplength=280
        ).grid(row=2, column=0, pady=(6, 26))


def build_field(master, label_text: str, placeholder: str = "", width: int = 0):
    """A labelled entry. Returns the container so the caller places it, and the entry
    so the caller reads it."""
    container = customtkinter.CTkFrame(master, fg_color="transparent")
    container.grid_columnconfigure(0, weight=1)

    customtkinter.CTkLabel(
        container,
        text=label_text.upper(),
        font=theme.font("overline"),
        text_color=theme.TEXT_MUTED,
        anchor="w",
    ).grid(row=0, column=0, sticky="ew", pady=(0, 5))

    entry = customtkinter.CTkEntry(
        container,
        placeholder_text=placeholder,
        height=38,
        corner_radius=theme.CONTROL_RADIUS,
        fg_color=theme.ENTRY_FILL,
        border_color=theme.ENTRY_BORDER,
        border_width=1,
        text_color=theme.TEXT_PRIMARY,
        placeholder_text_color=theme.TEXT_MUTED,
        font=theme.font("body"),
    )
    if width:
        entry.configure(width=width)
    entry.grid(row=1, column=0, sticky="ew")

    entry.bind("<FocusIn>", lambda _event: entry.configure(border_color=theme.FOCUS_RING, border_width=2))
    entry.bind("<FocusOut>", lambda _event: entry.configure(border_color=theme.ENTRY_BORDER, border_width=1))

    return container, entry


def build_primary_button(master, text: str, command) -> customtkinter.CTkButton:
    return customtkinter.CTkButton(
        master,
        text=text,
        command=command,
        height=38,
        corner_radius=theme.CONTROL_RADIUS,
        fg_color=theme.ACCENT,
        hover_color=theme.ACCENT_HOVER,
        text_color=theme.ACCENT_TEXT,
        font=theme.font("body_strong"),
    )


def build_danger_button(master, text: str, command, width: int = 88) -> customtkinter.CTkButton:
    return customtkinter.CTkButton(
        master,
        text=text,
        command=command,
        width=width,
        height=32,
        corner_radius=theme.CONTROL_RADIUS,
        fg_color="transparent",
        hover_color=theme.DANGER_SOFT,
        text_color=theme.DANGER,
        border_width=1,
        border_color=theme.BORDER,
        font=theme.font("caption"),
    )
