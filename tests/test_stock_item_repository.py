from src.models.stock_item import StockItem
from src.repositories.stock_item_repository import StockItemRepository


def test_save_assigns_an_id_to_the_item(db_connection):
    repository = StockItemRepository(db_connection)
    item = StockItem(name="Cimento", description="Saco 50kg", quantity_in_stock=10, unit_price=32.5)

    saved_item = repository.save(item)

    assert saved_item.id is not None


def test_find_by_id_returns_the_saved_item(db_connection):
    repository = StockItemRepository(db_connection)
    saved_item = repository.save(
        StockItem(name="Areia", description="Saco 20kg", quantity_in_stock=5, unit_price=15.0)
    )

    found_item = repository.find_by_id(saved_item.id)

    assert found_item == saved_item


def test_find_by_partial_name_matches_substring(db_connection):
    repository = StockItemRepository(db_connection)
    repository.save(StockItem(name="Cimento CPII", description="", quantity_in_stock=1, unit_price=1))
    repository.save(StockItem(name="Cal hidratada", description="", quantity_in_stock=1, unit_price=1))

    items = repository.find_by_partial_name("cimento")

    assert [item.name for item in items] == ["Cimento CPII"]


def test_update_quantity_in_stock_persists_the_new_value(db_connection):
    repository = StockItemRepository(db_connection)
    saved_item = repository.save(
        StockItem(name="Tijolo", description="", quantity_in_stock=100, unit_price=0.8)
    )

    repository.update_quantity_in_stock(saved_item.id, 90)

    assert repository.find_by_id(saved_item.id).quantity_in_stock == 90


def test_delete_removes_the_item(db_connection):
    repository = StockItemRepository(db_connection)
    saved_item = repository.save(
        StockItem(name="Prego", description="", quantity_in_stock=1, unit_price=1)
    )

    repository.delete(saved_item.id)

    assert repository.find_by_id(saved_item.id) is None
