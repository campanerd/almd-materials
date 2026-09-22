from dataclasses import dataclass
from typing import Optional


@dataclass
class Customer:
    full_name: str
    address: str
    phone_number: str
    id: Optional[int] = None
