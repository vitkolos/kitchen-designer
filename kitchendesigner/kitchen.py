from dataclasses import dataclass
from typing import List


@dataclass
class KitchenItem:
    name: str
    zone: str
    width_min: int
    width_max: int

    def __repr__(self) -> str:
        return self.name


@dataclass
class KitchenSegment:
    id: int
    width: int
    item: KitchenItem | None


@dataclass
class KitchenPart:
    width: int
    depth: int
    segments: List[KitchenSegment]


@dataclass
class Kitchen:
    items: List[KitchenItem]
    parts: List[KitchenPart]
