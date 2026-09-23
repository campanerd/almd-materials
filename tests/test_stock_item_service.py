from pathlib import Path

import pytest

from src.models.customer import Customer
from src.repositories.customer_repository import CustomerRepository
from src.repositories.sale_repository import SaleRepository
from src.repositories.stock_item_repository import StockItemRepository
from src.services.sale_service import ItemToSell, SaleService
from src.services.stock_item_service import InvalidStockItemDataError, StockItemService


@pytest.fixture
def stock_item_service(db_connection, tmp_path):
    images_folder = tmp_path / "item_images"
    return StockItemService(StockItemRepository(db_connection), images_folder=images_folder)


def test_register_item_stores_a_new_item(stock_item_service):
    item = stock_item_service.register_item("Cimento", "Saco 50kg", 10, 32.5)

    assert item.id is not None
    assert stock_item_service.find_item_by_id(item.id).name == "Cimento"


def test_register_item_copies_the_image_into_the_data_folder(stock_item_service, tmp_path):
    original_image = tmp_path / "cimento.png"
    original_image.write_bytes(b"fake image bytes")

    item = stock_item_service.register_item(
        "Cimento", "Saco 50kg", 10, 32.5, original_image_path=str(original_image)
    )

    assert item.image_path is not None
    assert Path(item.image_path).exists()
    assert Path(item.image_path) != original_image


def test_register_item_rejects_negative_quantity(stock_item_service):
    with pytest.raises(InvalidStockItemDataError):
        stock_item_service.register_item("Cimento", "Saco 50kg", -1, 32.5)


def test_register_item_rejects_negative_price(stock_item_service):
    with pytest.raises(InvalidStockItemDataError):
        stock_item_service.register_item("Cimento", "Saco 50kg", 10, -1)


def test_register_item_rejects_name_longer_than_the_limit(stock_item_service):
    with pytest.raises(InvalidStockItemDataError):
        stock_item_service.register_item("C" * 121, "Saco 50kg", 10, 32.5)


def test_register_item_rejects_description_longer_than_the_limit(stock_item_service):
    with pytest.raises(InvalidStockItemDataError):
        stock_item_service.register_item("Cimento", "D" * 301, 10, 32.5)


def test_register_item_rejects_an_image_path_that_does_not_exist(stock_item_service, tmp_path):
    missing_image = tmp_path / "does_not_exist.png"

    with pytest.raises(InvalidStockItemDataError):
        stock_item_service.register_item(
            "Cimento", "Saco 50kg", 10, 32.5, original_image_path=str(missing_image)
        )


def test_update_item_persists_the_new_data(stock_item_service):
    item = stock_item_service.register_item("Cimento", "Saco 50kg", 10, 32.5)

    item.unit_price = 40.0
    stock_item_service.update_item(item)

    assert stock_item_service.find_item_by_id(item.id).unit_price == 40.0


def test_delete_item_removes_the_item(stock_item_service):
    item = stock_item_service.register_item("Cimento", "Saco 50kg", 10, 32.5)

    stock_item_service.delete_item(item.id)

    assert stock_item_service.find_item_by_id(item.id) is None


def test_delete_item_rejects_when_item_has_been_sold(db_connection, stock_item_service):
    item = stock_item_service.register_item("Cimento", "Saco 50kg", 10, 32.5)
    customer = CustomerRepository(db_connection).save(
        Customer(full_name="Marcos", address="Rua M", phone_number="11977776666")
    )
    sale_service = SaleService(SaleRepository(db_connection), StockItemRepository(db_connection))
    sale_service.register_sale(customer.id, [ItemToSell(item.id, 1)])

    with pytest.raises(InvalidStockItemDataError):
        stock_item_service.delete_item(item.id)
