from src.models.customer import Customer
from src.models.sale import Sale, SoldItem
from src.models.stock_item import StockItem
from src.repositories.customer_repository import CustomerRepository
from src.repositories.sale_repository import SaleRepository
from src.repositories.stock_item_repository import StockItemRepository


def _create_customer_and_item(db_connection):
    customer = CustomerRepository(db_connection).save(
        Customer(full_name="Fernanda", address="Rua F", phone_number="1")
    )
    item = StockItemRepository(db_connection).save(
        StockItem(name="Cimento", description="", quantity_in_stock=50, unit_price=30.0)
    )
    return customer, item


def test_save_persists_the_sale_and_its_sold_items(db_connection):
    customer, item = _create_customer_and_item(db_connection)
    repository = SaleRepository(db_connection)
    sale = Sale(
        customer_id=customer.id,
        sold_items=[SoldItem(stock_item_id=item.id, quantity_sold=3, unit_price_at_sale_time=30.0)],
    )

    saved_sale = repository.save(sale)

    found_sale = repository.find_by_id(saved_sale.id)
    assert found_sale.customer_id == customer.id
    assert len(found_sale.sold_items) == 1
    assert found_sale.sold_items[0].quantity_sold == 3
    assert found_sale.total_amount == 90.0


def test_find_purchase_history_by_customer_orders_most_recent_first(db_connection):
    customer, item = _create_customer_and_item(db_connection)
    repository = SaleRepository(db_connection)

    first_sale = repository.save(
        Sale(customer_id=customer.id, sold_items=[SoldItem(item.id, 1, 30.0)])
    )
    second_sale = repository.save(
        Sale(customer_id=customer.id, sold_items=[SoldItem(item.id, 2, 30.0)])
    )

    history = repository.find_purchase_history_by_customer(customer.id)

    assert [sale.id for sale in history] == [second_sale.id, first_sale.id]
