import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent


def resource_path(*parts: str) -> Path:
    """Bundled read-only resource (assets, schema.sql).

    Resolves inside PyInstaller's extracted bundle when frozen, or the source tree
    when running from Python directly.
    """
    base = Path(sys._MEIPASS) if getattr(sys, "frozen", False) else PROJECT_ROOT
    return base.joinpath(*parts)


def persistent_data_path(*parts: str) -> Path:
    """Writable data that must survive between runs (the database, item images).

    A PyInstaller onefile executable extracts itself into a fresh temporary folder
    on every launch and deletes it on exit, so anything written under that folder is
    lost the moment the app closes. This anchors on the executable's own folder
    instead, which stays the same across launches.
    """
    base = Path(sys.executable).parent if getattr(sys, "frozen", False) else PROJECT_ROOT
    return base.joinpath(*parts)
