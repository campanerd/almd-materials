from src.models.customer import Customer
from src.repositories.customer_repository import CustomerRepository


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
        self.customer_repository.delete(id)

    @staticmethod
    def _validate_customer_data(full_name: str, address: str, phone_number: str) -> None:
        if not full_name:
            raise InvalidCustomerDataError("O nome do cliente é obrigatório.")
        if not address:
            raise InvalidCustomerDataError("O endereço do cliente é obrigatório.")
        if not phone_number:
            raise InvalidCustomerDataError("O telefone do cliente é obrigatório.")
