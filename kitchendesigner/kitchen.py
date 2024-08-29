from __future__ import annotations
from dataclasses import dataclass, field


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
    part: KitchenPart
    width: float
    fixture: Fixture | None
    is_first: bool
    is_last: bool
    previous: Segment | None = field(repr=False)

    def __str__(self) -> str:
        return 'segment' + str(self.number)

    def __hash__(self) -> int:
        return id(self)


@dataclass
class Position:
    x: float
    y: float
    angle: float
    group_number: int
    group_offset: float


@dataclass
class KitchenPart:
    name: str
    is_top: bool
    position: Position
    width: float
    depth: float
    edge_left: bool
    edge_right: bool
    segments: list[Segment]

    def __str__(self) -> str:
        return self.name

    def __hash__(self) -> int:
        return id(self)


@dataclass
class Rule:
    type: str
    area: str
    attribute_name: str
    attribute_value: str
    group: int = 0
    section_offset: float = 0
    section_width: float = 0

    def __str__(self) -> str:
        return f"{self.type}/{self.area}/{self.attribute_name}={self.attribute_value};{self.group},{self.section_offset},{self.section_width}"

    def __hash__(self) -> int:
        return id(self)

@dataclass
class Kitchen:
    groups: list[int]
    parts: list[KitchenPart]
    segments: list[Segment]
    rules: list[Rule]
    fixtures: list[Fixture]
