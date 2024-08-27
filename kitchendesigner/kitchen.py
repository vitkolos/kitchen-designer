from __future__ import annotations
from dataclasses import dataclass
from typing import List


@dataclass
class Fixture:
    name: str
    type: str
    zone: str
    width_min: float
    width_max: float
    is_top: bool
    has_worktop: bool
    allow_edge: bool
    complementary_fixture: Fixture | None = None

    def __str__(self) -> str:
        return self.name

    def __hash__(self) -> int:
        # used in Pyomo
        # https://stackoverflow.com/a/55086062/7530056
        return id(self)


@dataclass
class Segment:
    number: int
    width: float
    fixture: Fixture | None
    is_edge: bool
    is_first: bool
    is_top: bool
    previous: Segment | None

    def __str__(self) -> str:
        return 'segment' + str(self.number)

    def __hash__(self) -> int:
        return id(self)


@dataclass
class KitchenPart:
    name: str
    width: float
    depth: float
    segments: List[Segment]

    def __str__(self) -> str:
        return self.name

    def __hash__(self) -> int:
        return id(self)


@dataclass
class Kitchen:
    parts: List[KitchenPart]
    segments: List[Segment]
    fixtures: List[Fixture]
