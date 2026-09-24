"""Modal dialogs built on CTkToplevel.

tkinter.messagebox and the other native dialogs never follow the appearance mode --
they stay light grey while the rest of the app is dark -- so confirmations are built
here instead.
"""

import customtkinter

from src.interface import theme
from src.interface.animation import animate
from src.interface.components import FacetRule, build_primary_button

FADE_DURATION_MS = 170


class ModalDialog(customtkinter.CTkToplevel):
    def __init__(self, parent, title: str, width: int, height: int):
        super().__init__(parent)
        self.attributes("-alpha", 0.0)
        self.transient(parent)
        self.title(title)
        self.geometry(f"{width}x{height}")
        self.resizable(False, False)
        self.configure(fg_color=theme.BG_CANVAS)
        theme.apply_window_icon(self)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        FacetRule(self, height=3).grid(row=0, column=0, sticky="ew")

        customtkinter.CTkLabel(
            self,
            text=title,
            font=theme.font("title"),
            text_color=theme.TEXT_PRIMARY,
            anchor="w",
        ).grid(row=1, column=0, sticky="ew", padx=26, pady=(20, 4))

        self.body = customtkinter.CTkFrame(self, fg_color="transparent")
        self.body.grid(row=2, column=0, sticky="nsew", padx=26, pady=(10, 0))
        self.body.grid_columnconfigure(0, weight=1)

        self.footer = customtkinter.CTkFrame(self, fg_color="transparent")
        self.footer.grid(row=3, column=0, sticky="ew", padx=26, pady=(16, 20))
        self.footer.grid_columnconfigure(0, weight=1)

        self.bind("<Escape>", lambda _event: self.close())

    def show(self) -> None:
        self.grab_set()
        self._center_over_parent()
        animate(self, FADE_DURATION_MS, lambda progress: self.attributes("-alpha", progress))
        self.master.wait_window(self)

    def _center_over_parent(self) -> None:
        self.update_idletasks()
        parent = self.master
        target_x = parent.winfo_rootx() + (parent.winfo_width() - self.winfo_width()) // 2
        target_y = parent.winfo_rooty() + (parent.winfo_height() - self.winfo_height()) // 3
        self.geometry(f"+{target_x}+{target_y}")

        # geometry() positions the outer frame while winfo_rootx reports the client
        # area, so the first placement lands short by the border and titlebar.
        self.update_idletasks()
        self.geometry(
            f"+{target_x - (self.winfo_rootx() - target_x)}"
            f"+{target_y - (self.winfo_rooty() - target_y)}"
        )

    def close(self) -> None:
        self.grab_release()
        self.destroy()

    def add_cancel_button(self, text: str = "Cancelar") -> customtkinter.CTkButton:
        button = customtkinter.CTkButton(
            self.footer,
            text=text,
            command=self.close,
            height=38,
            width=110,
            corner_radius=theme.CONTROL_RADIUS,
            fg_color="transparent",
            hover_color=theme.ROW_HOVER,
            text_color=theme.TEXT_SECONDARY,
            border_width=1,
            border_color=theme.BORDER,
            font=theme.font("body"),
        )
        button.grid(row=0, column=1, padx=(0, 8))
        return button


class ConfirmationDialog(ModalDialog):
    def __init__(self, parent, title: str, message: str, confirm_text: str, destructive: bool = True):
        super().__init__(parent, title, width=460, height=250)
        self.confirmed = False

        customtkinter.CTkLabel(
            self.body,
            text=message,
            font=theme.font("body"),
            text_color=theme.TEXT_SECONDARY,
            anchor="w",
            justify="left",
            wraplength=400,
        ).grid(row=0, column=0, sticky="ew")

        self.add_cancel_button()

        confirm_button = customtkinter.CTkButton(
            self.footer,
            text=confirm_text,
            command=self._confirm,
            height=38,
            width=150,
            corner_radius=theme.CONTROL_RADIUS,
            fg_color=theme.DANGER if destructive else theme.ACCENT,
            hover_color=theme.DANGER_HOVER if destructive else theme.ACCENT_HOVER,
            text_color=theme.DANGER_TEXT if destructive else theme.ACCENT_TEXT,
            font=theme.font("body_strong"),
        )
        confirm_button.grid(row=0, column=2)

    def _confirm(self) -> None:
        self.confirmed = True
        self.close()


def ask_confirmation(parent, title: str, message: str, confirm_text: str) -> bool:
    dialog = ConfirmationDialog(parent, title, message, confirm_text)
    dialog.show()
    return dialog.confirmed


def show_error(parent, title: str, message: str) -> None:
    dialog = ModalDialog(parent, title, width=460, height=240)

    customtkinter.CTkLabel(
        dialog.body,
        text=message,
        font=theme.font("body"),
        text_color=theme.TEXT_SECONDARY,
        anchor="w",
        justify="left",
        wraplength=400,
    ).grid(row=0, column=0, sticky="ew")

    close_button = build_primary_button(dialog.footer, "Entendi", dialog.close)
    close_button.configure(width=130)
    close_button.grid(row=0, column=1)

    dialog.show()
