import pytest

from src.models.stock_item import StockItem
from src.repositories.customer_repository import CustomerRepository
from src.repositories.sale_repository import SaleRepository
from src.repositories.stock_item_repository import StockItemRepository
from src.services.customer_service import CustomerService, InvalidCustomerDataError
from src.services.sale_service import ItemToSell, SaleService


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


def test_update_customer_persists_the_new_data(customer_service):
    customer = customer_service.register_customer("Marcos", "Rua Antiga", "11977776666")

    customer.address = "Rua Nova"
    customer_service.update_customer(customer)

    assert customer_service.find_customer_by_id(customer.id).address == "Rua Nova"


def test_delete_customer_removes_the_customer(customer_service):
    customer = customer_service.register_customer("Marcos", "Rua M", "11977776666")

    customer_service.delete_customer(customer.id)

    assert customer_service.find_customer_by_id(customer.id) is None


def test_delete_customer_rejects_when_customer_has_purchase_history(db_connection, customer_service):
    customer = customer_service.register_customer("Marcos", "Rua M", "11977776666")
    stock_item_repository = StockItemRepository(db_connection)
    item = stock_item_repository.save(
        StockItem(name="Cimento", description="", quantity_in_stock=10, unit_price=30.0)
    )
    sale_service = SaleService(SaleRepository(db_connection), stock_item_repository)
    sale_service.register_sale(customer.id, [ItemToSell(item.id, 1)])

    with pytest.raises(InvalidCustomerDataError):
        customer_service.delete_customer(customer.id)
