from dataclasses import dataclass

from src.models.sale import Sale, SoldItem
from src.repositories.stock_item_repository import StockItemRepository
from src.repositories.sale_repository import SaleRepository


class InvalidSaleDataError(Exception):
    pass


class InsufficientStockError(Exception):
    pass


@dataclass
class ItemToSell:
    stock_item_id: int
    desired_quantity: int


class SaleService:
    def __init__(
        self,
        sale_repository: SaleRepository,
        stock_item_repository: StockItemRepository,
    ):
        self.sale_repository = sale_repository
        self.stock_item_repository = stock_item_repository

    def register_sale(self, customer_id: int, items_to_sell: list[ItemToSell]) -> Sale:
        if not items_to_sell:
            raise InvalidSaleDataError("A venda precisa ter ao menos um item.")

        reserved_quantity_by_stock_item_id: dict[int, int] = {}
        sold_items = [
            self._convert_to_sold_item(item_to_sell, reserved_quantity_by_stock_item_id)
            for item_to_sell in items_to_sell
        ]

        sale = Sale(customer_id=customer_id, sold_items=sold_items)
        sale = self.sale_repository.save(sale)

        for item_to_sell in items_to_sell:
            self._debit_quantity_from_stock(item_to_sell.stock_item_id, item_to_sell.desired_quantity)

        return sale

    def list_purchase_history_by_customer(self, customer_id: int) -> list[Sale]:
        return self.sale_repository.find_purchase_history_by_customer(customer_id)

    def _convert_to_sold_item(
        self, item_to_sell: ItemToSell, reserved_quantity_by_stock_item_id: dict[int, int]
    ) -> SoldItem:
        if item_to_sell.desired_quantity <= 0:
            raise InvalidSaleDataError("A quantidade vendida precisa ser maior que zero.")

        stock_item = self.stock_item_repository.find_by_id(item_to_sell.stock_item_id)
        if stock_item is None:
            raise InvalidSaleDataError(f"Item de estoque {item_to_sell.stock_item_id} não encontrado.")

        already_reserved_quantity = reserved_quantity_by_stock_item_id.get(item_to_sell.stock_item_id, 0)
        total_requested_quantity = already_reserved_quantity + item_to_sell.desired_quantity
        if stock_item.quantity_in_stock < total_requested_quantity:
            raise InsufficientStockError(
                f"Estoque insuficiente para o item '{stock_item.name}'. "
                f"Disponível: {stock_item.quantity_in_stock}, "
                f"solicitado: {total_requested_quantity}."
            )
        reserved_quantity_by_stock_item_id[item_to_sell.stock_item_id] = total_requested_quantity

        return SoldItem(
            stock_item_id=stock_item.id,
            quantity_sold=item_to_sell.desired_quantity,
            unit_price_at_sale_time=stock_item.unit_price,
        )

    def _debit_quantity_from_stock(self, stock_item_id: int, quantity_sold: int) -> None:
        stock_item = self.stock_item_repository.find_by_id(stock_item_id)
        new_quantity = stock_item.quantity_in_stock - quantity_sold
        self.stock_item_repository.update_quantity_in_stock(stock_item_id, new_quantity)
