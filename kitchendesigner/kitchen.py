from dataclasses import dataclass
from typing import List

@dataclass
class KitchenItem:
    name: str
    zone: str
    width_min: int
    width_max: int

@dataclass
class Kitchen:
    width: int
    items: List[KitchenItem]
