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
    customer = customer_service.register_customer("  Marcos  ", "  Rua M  ", "  11977776666  ")

    assert customer.full_name == "Marcos"
    assert customer.address == "Rua M"
    assert customer.phone_number == "11977776666"


@pytest.mark.parametrize(
    "full_name,address,phone_number",
    [
        ("", "Rua M", "11977776666"),
        ("Marcos", "", "11977776666"),
        ("Marcos", "Rua M", ""),
    ],
)
def test_register_customer_rejects_missing_required_fields(customer_service, full_name, address, phone_number):
    with pytest.raises(InvalidCustomerDataError):
        customer_service.register_customer(full_name, address, phone_number)


def test_register_customer_accepts_formatted_phone_number(customer_service):
    customer = customer_service.register_customer("Marcos", "Rua M", "(11) 91234-5678")

    assert customer.phone_number == "(11) 91234-5678"


@pytest.mark.parametrize("phone_number", ["123", "123456789012", "abc-defg-hijk"])
def test_register_customer_rejects_phone_number_with_wrong_digit_count(customer_service, phone_number):
    with pytest.raises(InvalidCustomerDataError):
        customer_service.register_customer("Marcos", "Rua M", phone_number)


def test_register_customer_rejects_name_longer_than_the_limit(customer_service):
    with pytest.raises(InvalidCustomerDataError):
        customer_service.register_customer("A" * 121, "Rua M", "11977776666")


def test_register_customer_rejects_address_longer_than_the_limit(customer_service):
    with pytest.raises(InvalidCustomerDataError):
        customer_service.register_customer("Marcos", "R" * 201, "11977776666")
