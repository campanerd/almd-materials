import pytest

from src.repositories.customer_repository import CustomerRepository
from src.repositories.sale_repository import SaleRepository
from src.repositories.stock_item_repository import StockItemRepository
from src.services.sale_service import (
    InsufficientStockError,
    InvalidSaleDataError,
    ItemToSell,
    SaleService,
)


@pytest.fixture
def customer_id(db_connection):
    from src.models.customer import Customer

    customer = CustomerRepository(db_connection).save(
        Customer(full_name="Fernanda", address="Rua F", phone_number="1")
    )
    return customer.id


@pytest.fixture
def stock_item_repository(db_connection):
    return StockItemRepository(db_connection)


@pytest.fixture
def sale_service(db_connection, stock_item_repository):
    return SaleService(SaleRepository(db_connection), stock_item_repository)


def _create_stock_item(stock_item_repository, quantity_in_stock=10, unit_price=30.0):
    from src.models.stock_item import StockItem

    return stock_item_repository.save(
        StockItem(name="Cimento", description="", quantity_in_stock=quantity_in_stock, unit_price=unit_price)
    )


def test_register_sale_creates_a_sale_with_the_correct_total(sale_service, stock_item_repository, customer_id):
    item = _create_stock_item(stock_item_repository, quantity_in_stock=10, unit_price=30.0)

    sale = sale_service.register_sale(customer_id, [ItemToSell(item.id, 3)])

    assert sale.id is not None
    assert sale.total_amount == 90.0


def test_register_sale_debits_the_quantity_from_stock(sale_service, stock_item_repository, customer_id):
    item = _create_stock_item(stock_item_repository, quantity_in_stock=10, unit_price=30.0)

    sale_service.register_sale(customer_id, [ItemToSell(item.id, 3)])

    assert stock_item_repository.find_by_id(item.id).quantity_in_stock == 7


def test_register_sale_rejects_when_stock_is_insufficient(sale_service, stock_item_repository, customer_id):
    item = _create_stock_item(stock_item_repository, quantity_in_stock=2, unit_price=30.0)

    with pytest.raises(InsufficientStockError):
        sale_service.register_sale(customer_id, [ItemToSell(item.id, 5)])


def test_register_sale_rejects_an_empty_cart(sale_service, customer_id):
    with pytest.raises(InvalidSaleDataError):
        sale_service.register_sale(customer_id, [])


def test_register_sale_rejects_when_the_same_item_repeated_in_the_cart_exceeds_stock(
    sale_service, stock_item_repository, customer_id
):
    item = _create_stock_item(stock_item_repository, quantity_in_stock=10, unit_price=30.0)

    with pytest.raises(InsufficientStockError):
        sale_service.register_sale(customer_id, [ItemToSell(item.id, 6), ItemToSell(item.id, 6)])

    assert stock_item_repository.find_by_id(item.id).quantity_in_stock == 10


def test_list_purchase_history_by_customer_returns_registered_sales(sale_service, stock_item_repository, customer_id):
    item = _create_stock_item(stock_item_repository)
    sale_service.register_sale(customer_id, [ItemToSell(item.id, 1)])

    history = sale_service.list_purchase_history_by_customer(customer_id)

    assert len(history) == 1


def test_cancel_sale_returns_the_quantity_to_stock(sale_service, stock_item_repository, customer_id):
    item = _create_stock_item(stock_item_repository, quantity_in_stock=10, unit_price=30.0)
    sale = sale_service.register_sale(customer_id, [ItemToSell(item.id, 3)])

    sale_service.cancel_sale(sale.id)

    assert stock_item_repository.find_by_id(item.id).quantity_in_stock == 10


def test_cancel_sale_marks_the_sale_as_cancelled(sale_service, stock_item_repository, customer_id):
    item = _create_stock_item(stock_item_repository)
    sale = sale_service.register_sale(customer_id, [ItemToSell(item.id, 1)])

    cancelled_sale = sale_service.cancel_sale(sale.id)

    assert cancelled_sale.is_cancelled


def test_cancel_sale_rejects_an_already_cancelled_sale(sale_service, stock_item_repository, customer_id):
    item = _create_stock_item(stock_item_repository)
    sale = sale_service.register_sale(customer_id, [ItemToSell(item.id, 1)])
    sale_service.cancel_sale(sale.id)

    with pytest.raises(InvalidSaleDataError):
        sale_service.cancel_sale(sale.id)


def test_cancel_sale_rejects_a_nonexistent_sale(sale_service):
    with pytest.raises(InvalidSaleDataError):
        sale_service.cancel_sale(999)
