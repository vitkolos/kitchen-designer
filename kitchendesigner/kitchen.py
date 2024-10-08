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
    storage: float
    has_worktop: bool
    allow_edge: bool
    is_corner: bool = False
    complementary_fixture: Fixture | None = None
    second_corner_fixture: Fixture | None = None
    older_sibling: Fixture | None = field(default=None, repr=False)

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
    width: float  # <- solution
    fixture: Fixture | None  # <- solution
    is_first: bool
    is_last: bool
    previous: Segment | None = field(repr=False)
    next: Segment | None = field(repr=False, default=None)

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
    padding: float = 0  # <- solution


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
class PlacementRule:
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
class RelationRules:
    targets: dict[str, tuple[float, float]]
    min_distances: dict[tuple[str, str], float]
    wall_distances: dict[str, float]
    min_worktops: dict[str, float]
    one_wide: dict[str, float]


@dataclass
class Corner:
    part1: KitchenPart
    part1_left: bool
    part2: KitchenPart
    part2_left: bool

    def __str__(self) -> str:
        return f"{self.part1}/{self.part2}"

    def __hash__(self) -> int:
        return id(self)


@dataclass
class Wall:
    group: int
    left: float
    right: float


@dataclass
class Zone:
    name: str
    is_optimized: bool
    optimal_center: tuple[float, float] | None
    color: str


@dataclass
class Constants:
    min_fixture_width: float = 0
    max_fixture_width: float = 0
    max_canvas_size: float = 0
    vertical_continuity_tolerance: float = 0
    width_same_tolerance: float = 0
    width_different_tolerance: float = 0
    width_penult_similar_tolerance: float = 0
    max_segment_count: int = 0

@dataclass
class Preferences:
    storage: float = 1
    worktop: float = 1

@dataclass
class Kitchen:
    groups: list[int]
    parts: list[KitchenPart]
    segments: list[Segment]
    walls: dict[int, Wall]
    corners: list[Corner]
    placement_rules: list[PlacementRule]
    relation_rules: RelationRules
    preferences: Preferences
    constants: Constants
    zones: list[Zone]
    fixtures: list[Fixture]
