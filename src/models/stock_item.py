from dataclasses import dataclass
from typing import Optional


@dataclass
class StockItem:
    name: str
    description: str
    quantity_in_stock: int
    unit_price: float
    image_path: Optional[str] = None
    id: Optional[int] = None
