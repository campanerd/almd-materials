import sqlite3

from src.models.customer import Customer


class CustomerRepository:
    def __init__(self, connection: sqlite3.Connection):
        self.connection = connection

    def save(self, customer: Customer) -> Customer:
        cursor = self.connection.execute(
            """
            INSERT INTO customer (full_name, address, phone_number)
            VALUES (?, ?, ?)
            """,
            (customer.full_name, customer.address, customer.phone_number),
        )
        self.connection.commit()
        customer.id = cursor.lastrowid
        return customer

    def find_by_id(self, id: int) -> Customer | None:
        row = self.connection.execute(
            "SELECT * FROM customer WHERE id = ?", (id,)
        ).fetchone()
        return self._row_to_customer(row) if row else None

    def find_all(self) -> list[Customer]:
        rows = self.connection.execute(
            "SELECT * FROM customer ORDER BY full_name"
        ).fetchall()
        return [self._row_to_customer(row) for row in rows]

    def find_by_partial_name(self, name_fragment: str) -> list[Customer]:
        rows = self.connection.execute(
            "SELECT * FROM customer WHERE full_name LIKE ? ORDER BY full_name",
            (f"%{name_fragment}%",),
        ).fetchall()
        return [self._row_to_customer(row) for row in rows]

    def update(self, customer: Customer) -> None:
        self.connection.execute(
            """
            UPDATE customer
            SET full_name = ?, address = ?, phone_number = ?
            WHERE id = ?
            """,
            (customer.full_name, customer.address, customer.phone_number, customer.id),
        )
        self.connection.commit()

    def delete(self, id: int) -> None:
        self.connection.execute("DELETE FROM customer WHERE id = ?", (id,))
        self.connection.commit()

    @staticmethod
    def _row_to_customer(row: sqlite3.Row) -> Customer:
        return Customer(
            id=row["id"],
            full_name=row["full_name"],
            address=row["address"],
            phone_number=row["phone_number"],
        )
