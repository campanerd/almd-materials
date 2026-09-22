import pytest

from src.repositories.customer_repository import CustomerRepository
from src.services.customer_service import CustomerService, InvalidCustomerDataError


@pytest.fixture
def customer_service(db_connection):
    return CustomerService(CustomerRepository(db_connection))


def test_register_customer_stores_a_new_customer(customer_service):
    customer = customer_service.register_customer("Marcos Pereira", "Rua M, 10", "11977776666")

    assert customer.id is not None
    assert customer_service.find_customer_by_id(customer.id).full_name == "Marcos Pereira"


def test_register_customer_trims_whitespace_from_fields(customer_service):
    customer = customer_service.register_customer("  Marcos  ", "  Rua M  ", "  119  ")

    assert customer.full_name == "Marcos"
    assert customer.address == "Rua M"
    assert customer.phone_number == "119"


@pytest.mark.parametrize(
    "full_name,address,phone_number",
    [
        ("", "Rua M", "119"),
        ("Marcos", "", "119"),
        ("Marcos", "Rua M", ""),
    ],
)
def test_register_customer_rejects_missing_required_fields(customer_service, full_name, address, phone_number):
    with pytest.raises(InvalidCustomerDataError):
        customer_service.register_customer(full_name, address, phone_number)
