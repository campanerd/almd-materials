import re
import sqlite3

from src.models.customer import Customer
from src.repositories.customer_repository import CustomerRepository

MAX_FULL_NAME_LENGTH = 120
MAX_ADDRESS_LENGTH = 200
MIN_PHONE_DIGITS = 8
MAX_PHONE_DIGITS = 11


class InvalidCustomerDataError(Exception):
    pass


class CustomerService:
    def __init__(self, customer_repository: CustomerRepository):
        self.customer_repository = customer_repository

    def register_customer(self, full_name: str, address: str, phone_number: str) -> Customer:
        full_name = full_name.strip()
        address = address.strip()
        phone_number = phone_number.strip()

        self._validate_customer_data(full_name, address, phone_number)

        customer = Customer(full_name=full_name, address=address, phone_number=phone_number)
        return self.customer_repository.save(customer)

    def update_customer(self, customer: Customer) -> None:
        self._validate_customer_data(customer.full_name, customer.address, customer.phone_number)
        self.customer_repository.update(customer)

    def find_customer_by_id(self, id: int) -> Customer | None:
        return self.customer_repository.find_by_id(id)

    def list_all_customers(self) -> list[Customer]:
        return self.customer_repository.find_all()

    def find_customers_by_name(self, name_fragment: str) -> list[Customer]:
        return self.customer_repository.find_by_partial_name(name_fragment)

    def delete_customer(self, id: int) -> None:
        try:
            self.customer_repository.delete(id)
        except sqlite3.IntegrityError as error:
            raise InvalidCustomerDataError(
                "Não é possível excluir um cliente que já tem compras registradas."
            ) from error

    @classmethod
    def _validate_customer_data(cls, full_name: str, address: str, phone_number: str) -> None:
        if not full_name:
            raise InvalidCustomerDataError("O nome do cliente é obrigatório.")
        if len(full_name) > MAX_FULL_NAME_LENGTH:
            raise InvalidCustomerDataError(
                f"O nome do cliente não pode ter mais que {MAX_FULL_NAME_LENGTH} caracteres."
            )
        if not address:
            raise InvalidCustomerDataError("O endereço do cliente é obrigatório.")
        if len(address) > MAX_ADDRESS_LENGTH:
            raise InvalidCustomerDataError(
                f"O endereço não pode ter mais que {MAX_ADDRESS_LENGTH} caracteres."
            )
        if not phone_number:
            raise InvalidCustomerDataError("O telefone do cliente é obrigatório.")
        cls._validate_phone_number(phone_number)

    @staticmethod
    def _validate_phone_number(phone_number: str) -> None:
        digits_only = re.sub(r"\D", "", phone_number)
        if not (MIN_PHONE_DIGITS <= len(digits_only) <= MAX_PHONE_DIGITS):
            raise InvalidCustomerDataError(
                f"Telefone inválido. Informe entre {MIN_PHONE_DIGITS} e {MAX_PHONE_DIGITS} dígitos."
            )
