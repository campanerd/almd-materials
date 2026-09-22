import sqlite3

from src.models.stock_item import StockItem


class StockItemRepository:
    def __init__(self, connection: sqlite3.Connection):
        self.connection = connection

    def save(self, item: StockItem) -> StockItem:
        cursor = self.connection.execute(
            """
            INSERT INTO stock_item
                (name, description, quantity_in_stock, unit_price, image_path)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                item.name,
                item.description,
                item.quantity_in_stock,
                item.unit_price,
                item.image_path,
            ),
        )
        self.connection.commit()
        item.id = cursor.lastrowid
        return item

    def find_by_id(self, id: int) -> StockItem | None:
        row = self.connection.execute(
            "SELECT * FROM stock_item WHERE id = ?", (id,)
        ).fetchone()
        return self._row_to_stock_item(row) if row else None

    def find_all(self) -> list[StockItem]:
        rows = self.connection.execute(
            "SELECT * FROM stock_item ORDER BY name"
        ).fetchall()
        return [self._row_to_stock_item(row) for row in rows]

    def find_by_partial_name(self, name_fragment: str) -> list[StockItem]:
        rows = self.connection.execute(
            "SELECT * FROM stock_item WHERE name LIKE ? ORDER BY name",
            (f"%{name_fragment}%",),
        ).fetchall()
        return [self._row_to_stock_item(row) for row in rows]

    def update(self, item: StockItem) -> None:
        self.connection.execute(
            """
            UPDATE stock_item
            SET name = ?, description = ?, quantity_in_stock = ?,
                unit_price = ?, image_path = ?
            WHERE id = ?
            """,
            (
                item.name,
                item.description,
                item.quantity_in_stock,
                item.unit_price,
                item.image_path,
                item.id,
            ),
        )
        self.connection.commit()

    def update_quantity_in_stock(self, id: int, new_quantity: int) -> None:
        self.connection.execute(
            "UPDATE stock_item SET quantity_in_stock = ? WHERE id = ?",
            (new_quantity, id),
        )
        self.connection.commit()

    def delete(self, id: int) -> None:
        self.connection.execute("DELETE FROM stock_item WHERE id = ?", (id,))
        self.connection.commit()

    @staticmethod
    def _row_to_stock_item(row: sqlite3.Row) -> StockItem:
        return StockItem(
            id=row["id"],
            name=row["name"],
            description=row["description"],
            quantity_in_stock=row["quantity_in_stock"],
            unit_price=row["unit_price"],
            image_path=row["image_path"],
        )
