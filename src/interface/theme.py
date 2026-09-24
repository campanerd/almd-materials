"""Design tokens for the interface.

Every color is a ("#light", "#dark") tuple: CustomTkinter only swaps colors between
appearance modes when it receives a 2-tuple. A single literal hex string freezes in
whatever mode it was created in and silently breaks the theme switch.
"""

import customtkinter
from PIL import Image

from src.app_paths import resource_path

ASSETS_FOLDER = resource_path("assets")
WINDOW_ICON_PATH = ASSETS_FOLDER / "logo.ico"

BRAND_DEEP = ("#12592F", "#2E7A4C")
BRAND_MID = ("#4D8C66", "#5FB183")
BRAND_SAGE = ("#90B9A2", "#8FCFA8")

BG_CANVAS = ("#F2F6F3", "#0E1512")
BG_SIDEBAR = ("#EAF0EC", "#111917")
BG_CARD = ("#FFFFFF", "#151E1A")
BG_ELEVATED = ("#FFFFFF", "#1B2621")
ROW_HOVER = ("#EDF3EF", "#1F2C26")
THUMB_BG = ("#EDF3EF", "#1F2C26")

BORDER = ("#DCE5E0", "#243029")
DIVIDER = ("#E8EDEA", "#222E28")
ENTRY_BORDER = ("#7B998A", "#5C7266")
FOCUS_RING = ("#12592F", "#5FB183")
METER_TRACK = ("#E1EAE5", "#232F29")
SWITCH_TRACK = ("#C9D6CF", "#2E3D35")
SWITCH_KNOB = ("#FFFFFF", "#E9F1EC")

TEXT_PRIMARY = ("#14211B", "#E9F1EC")
TEXT_SECONDARY = ("#4A5B53", "#A7B8AF")
TEXT_MUTED = ("#5E6F66", "#99ABA2")
DISABLED_TEXT = ("#9DACA4", "#5A6B63")

ACCENT = ("#12592F", "#4D8C66")
ACCENT_HOVER = ("#0D4423", "#5FB183")
ACCENT_TEXT = ("#FFFFFF", "#08130C")
ACCENT_FG = ("#0F4D28", "#5FB183")
NAV_PILL = ("#12592F", "#1C3A29")
NAV_PILL_TEXT = ("#FFFFFF", "#E9F1EC")
ENTRY_FILL = ("#F7FAF8", "#111A16")

DANGER = ("#B3261E", "#E5695E")
DANGER_TEXT = ("#FFFFFF", "#2A0906")
DANGER_HOVER = ("#8C1D18", "#F2A39C")
DANGER_SOFT = ("#FBEAE9", "#2C1614")
SUCCESS = ("#1B6E3C", "#5FB183")
CHIP_OK = ("#E3EFE8", "#172C20")
CHIP_OK_TEXT = ("#0F4D28", "#8FCFA8")
CHIP_WARN = ("#FBF0DF", "#2C2213")
CHIP_WARN_TEXT = ("#6E4200", "#E8C089")
CHIP_DANGER = ("#FBEAE9", "#2C1614")
CHIP_DANGER_TEXT = ("#8C1D18", "#F2A39C")

HEADING_FAMILY = "Segoe UI Variable Display"
BODY_FAMILY = "Segoe UI Variable Text"
SMALL_FAMILY = "Segoe UI Variable Small"
NUMERIC_FAMILY = "Consolas"

SIDEBAR_WIDTH = 248
ROW_HEIGHT = 56
ROW_SPINE_WIDTH = 4
CARD_RADIUS = 14
CONTROL_RADIUS = 9

_font_cache: dict[str, customtkinter.CTkFont] = {}
_image_cache: dict[str, customtkinter.CTkImage] = {}


def font(role: str) -> customtkinter.CTkFont:
    """CTkFont instances need a live Tk root, so they are built on first use."""
    if role not in _font_cache:
        _font_cache[role] = _build_font(role)
    return _font_cache[role]


def _build_font(role: str) -> customtkinter.CTkFont:
    specs = {
        "display": (HEADING_FAMILY, 27, "normal"),
        "title": (HEADING_FAMILY, 19, "bold"),
        "brand": (HEADING_FAMILY, 16, "bold"),
        "section": (BODY_FAMILY, 15, "bold"),
        "body": (BODY_FAMILY, 13, "normal"),
        "body_strong": (BODY_FAMILY, 13, "bold"),
        "nav": (BODY_FAMILY, 14, "normal"),
        "caption": (SMALL_FAMILY, 12, "normal"),
        "overline": (SMALL_FAMILY, 11, "bold"),
        "numeric": (NUMERIC_FAMILY, 13, "normal"),
        "numeric_strong": (NUMERIC_FAMILY, 15, "bold"),
        "total": (NUMERIC_FAMILY, 26, "bold"),
    }
    family, size, weight = specs[role]
    return customtkinter.CTkFont(family=family, size=size, weight=weight)


def apply_window_icon(window) -> None:
    """Replaces the default Tk feather in the titlebar and the taskbar.

    CustomTkinter sets its own icon on a CTkToplevel shortly after the window is
    mapped, so the call is repeated on a delay or the default comes back.
    """

    def set_icon() -> None:
        try:
            window.iconbitmap(str(WINDOW_ICON_PATH))
        except Exception:
            pass

    set_icon()
    window.after(300, set_icon)


def logo_image(size: int) -> customtkinter.CTkImage:
    """The light asset keeps the logo's own tones; the dark one is lifted so the
    facets stay legible once the white gaps become a dark surface."""
    key = f"logo-{size}"
    if key not in _image_cache:
        _image_cache[key] = customtkinter.CTkImage(
            light_image=Image.open(ASSETS_FOLDER / "logo.png"),
            dark_image=Image.open(ASSETS_FOLDER / "logo_dark.png"),
            size=(size, size),
        )
    return _image_cache[key]
