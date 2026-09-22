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

        sold_items = [self._convert_to_sold_item(item_to_sell) for item_to_sell in items_to_sell]

        sale = Sale(customer_id=customer_id, sold_items=sold_items)
        sale = self.sale_repository.save(sale)

        for item_to_sell in items_to_sell:
            self._debit_quantity_from_stock(item_to_sell.stock_item_id, item_to_sell.desired_quantity)

        return sale

    def list_purchase_history_by_customer(self, customer_id: int) -> list[Sale]:
        return self.sale_repository.find_purchase_history_by_customer(customer_id)

    def _convert_to_sold_item(self, item_to_sell: ItemToSell) -> SoldItem:
        if item_to_sell.desired_quantity <= 0:
            raise InvalidSaleDataError("A quantidade vendida precisa ser maior que zero.")

        stock_item = self.stock_item_repository.find_by_id(item_to_sell.stock_item_id)
        if stock_item is None:
            raise InvalidSaleDataError(f"Item de estoque {item_to_sell.stock_item_id} não encontrado.")
        if stock_item.quantity_in_stock < item_to_sell.desired_quantity:
            raise InsufficientStockError(
                f"Estoque insuficiente para o item '{stock_item.name}'. "
                f"Disponível: {stock_item.quantity_in_stock}, "
                f"solicitado: {item_to_sell.desired_quantity}."
            )

        return SoldItem(
            stock_item_id=stock_item.id,
            quantity_sold=item_to_sell.desired_quantity,
            unit_price_at_sale_time=stock_item.unit_price,
        )

    def _debit_quantity_from_stock(self, stock_item_id: int, quantity_sold: int) -> None:
        stock_item = self.stock_item_repository.find_by_id(stock_item_id)
        new_quantity = stock_item.quantity_in_stock - quantity_sold
        self.stock_item_repository.update_quantity_in_stock(stock_item_id, new_quantity)
