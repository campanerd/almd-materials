import sqlite3
from pathlib import Path

from src.app_paths import persistent_data_path, resource_path

SCHEMA_FILE_PATH = resource_path("src", "database", "schema.sql")
DEFAULT_DATABASE_PATH = persistent_data_path("data", "store.db")


def create_database_connection(database_path: Path | str = DEFAULT_DATABASE_PATH) -> sqlite3.Connection:
    database_path = Path(database_path)
    if str(database_path) != ":memory:":
        database_path.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(database_path)
    connection.execute("PRAGMA foreign_keys = ON")
    connection.row_factory = sqlite3.Row

    schema_script = SCHEMA_FILE_PATH.read_text(encoding="utf-8")
    connection.executescript(schema_script)

    return connection
