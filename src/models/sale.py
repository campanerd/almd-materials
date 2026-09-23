from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class SoldItem:
    stock_item_id: int
    quantity_sold: int
    unit_price_at_sale_time: float
    id: Optional[int] = None

    @property
    def total_value(self) -> float:
        return self.quantity_sold * self.unit_price_at_sale_time


@dataclass
class Sale:
    customer_id: int
    sold_items: list[SoldItem] = field(default_factory=list)
    sale_date_time: datetime = field(default_factory=datetime.now)
    cancelled_at: Optional[datetime] = None
    id: Optional[int] = None

    @property
    def total_amount(self) -> float:
        return sum(item.total_value for item in self.sold_items)

    @property
    def is_cancelled(self) -> bool:
        return self.cancelled_at is not None
