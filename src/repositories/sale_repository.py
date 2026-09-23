import sqlite3
from datetime import datetime

from src.models.sale import Sale, SoldItem


class SaleRepository:
    def __init__(self, connection: sqlite3.Connection):
        self.connection = connection

    def save(self, sale: Sale) -> Sale:
        cursor = self.connection.execute(
            """
            INSERT INTO sale (customer_id, sale_date_time)
            VALUES (?, ?)
            """,
            (sale.customer_id, sale.sale_date_time.isoformat()),
        )
        sale.id = cursor.lastrowid

        for sold_item in sale.sold_items:
            self._save_sold_item(sale.id, sold_item)

        self.connection.commit()
        return sale

    def _save_sold_item(self, sale_id: int, sold_item: SoldItem) -> None:
        cursor = self.connection.execute(
            """
            INSERT INTO sold_item
                (sale_id, stock_item_id, quantity_sold, unit_price_at_sale_time)
            VALUES (?, ?, ?, ?)
            """,
            (
                sale_id,
                sold_item.stock_item_id,
                sold_item.quantity_sold,
                sold_item.unit_price_at_sale_time,
            ),
        )
        sold_item.id = cursor.lastrowid

    def find_by_id(self, id: int) -> Sale | None:
        sale_row = self.connection.execute(
            "SELECT * FROM sale WHERE id = ?", (id,)
        ).fetchone()
        if not sale_row:
            return None
        return self._row_to_sale(sale_row)

    def find_purchase_history_by_customer(self, customer_id: int) -> list[Sale]:
        sale_rows = self.connection.execute(
            """
            SELECT * FROM sale
            WHERE customer_id = ?
            ORDER BY sale_date_time DESC, id DESC
            """,
            (customer_id,),
        ).fetchall()
        return [self._row_to_sale(row) for row in sale_rows]

    def cancel(self, id: int, cancelled_at: datetime) -> None:
        self.connection.execute(
            "UPDATE sale SET cancelled_at = ? WHERE id = ?",
            (cancelled_at.isoformat(), id),
        )
        self.connection.commit()

    def _row_to_sale(self, sale_row: sqlite3.Row) -> Sale:
        sold_item_rows = self.connection.execute(
            "SELECT * FROM sold_item WHERE sale_id = ?",
            (sale_row["id"],),
        ).fetchall()

        sold_items = [
            SoldItem(
                id=row["id"],
                stock_item_id=row["stock_item_id"],
                quantity_sold=row["quantity_sold"],
                unit_price_at_sale_time=row["unit_price_at_sale_time"],
            )
            for row in sold_item_rows
        ]

        cancelled_at = (
            datetime.fromisoformat(sale_row["cancelled_at"]) if sale_row["cancelled_at"] else None
        )

        return Sale(
            id=sale_row["id"],
            customer_id=sale_row["customer_id"],
            sale_date_time=datetime.fromisoformat(sale_row["sale_date_time"]),
            sold_items=sold_items,
            cancelled_at=cancelled_at,
        )
