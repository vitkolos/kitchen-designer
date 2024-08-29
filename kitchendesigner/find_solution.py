from kitchen import *
from typing import Any, List
import pyomo.environ as pyo
import math
import sys

max_fixture_width = 100
max_canvas_size = 800
max_group_count = 50


def solve(kitchen: Kitchen) -> None:
    model = KitchenModel(kitchen)
    set_constraints(model)
    set_objective(model)
    find_model(model)
    save_result(kitchen, model)


class KitchenModel(pyo.ConcreteModel):  # type: ignore[misc]
    def __init__(model: pyo.ConcreteModel, kitchen: Kitchen) -> None:
        super().__init__()

        # sets
        model.fixtures = pyo.Set(initialize=kitchen.fixtures)
        model.segments = pyo.Set(initialize=kitchen.segments)
        model.parts = pyo.Set(initialize=kitchen.parts)

        # product variable
        model.pairs = pyo.Var(model.segments, model.fixtures, domain=pyo.Binary)

        # segment variables
        model.widths = pyo.Var(model.segments, domain=pyo.NonNegativeReals, bounds=(0, max_fixture_width))
        model.segments_x = pyo.Var(model.segments, domain=pyo.Reals, bounds=(-max_canvas_size, max_canvas_size))
        model.segments_y = pyo.Var(model.segments, domain=pyo.Reals, bounds=(-max_canvas_size, max_canvas_size))
        model.segments_offset = pyo.Var(model.segments, domain=pyo.NonNegativeReals, bounds=(0, max_canvas_size))

        # fixture variables
        model.present = pyo.Var(model.fixtures, domain=pyo.Binary)
        model.fixtures_x = pyo.Var(model.fixtures, domain=pyo.Reals, bounds=(-max_canvas_size, max_canvas_size))
        model.fixtures_y = pyo.Var(model.fixtures, domain=pyo.Reals, bounds=(-max_canvas_size, max_canvas_size))
        model.fixtures_width = pyo.Var(model.fixtures, domain=pyo.NonNegativeReals, bounds=(0, max_fixture_width))
        model.fixtures_offset = pyo.Var(model.fixtures, domain=pyo.NonNegativeReals, bounds=(0, max_fixture_width))
        model.fixtures_group = pyo.Var(model.fixtures, domain=pyo.NonNegativeIntegers, bounds=(0, max_group_count))


def set_constraints(model: KitchenModel) -> None:
    clause_count = 0

    def get_clause(clauses: List[Any], current_clause: int) -> Any:
        """simplifies defining multiple constraints in one function"""
        if current_clause == 1:
            clause_real_count = len(clauses)
            assert clause_real_count == clause_count, f"Expected {clause_count} clauses, found {clause_real_count}"
        return clauses[current_clause-1]

    # BASIC RULES

    def presence_pairs_pairing(model: KitchenModel, fixture: Fixture) -> Any:
        """fixture is present <=> it belongs to exactly one pair \n
        fixture is not present <=> it does not belong to any pair"""
        return model.present[fixture] == sum(model.pairs[segment, fixture] for segment in model.segments)

    model.presence_pairs_pairing = pyo.Constraint(model.fixtures, rule=presence_pairs_pairing)

    def segment_capacity(model: KitchenModel, segment: Segment) -> Any:
        """each segment can contain at most one fixture"""
        return sum(model.pairs[segment, fixture] for fixture in model.fixtures) <= 1

    model.segment_capacity = pyo.Constraint(model.segments, rule=segment_capacity)

    def previous_segment_zero(model: KitchenModel, segment: Segment) -> Any:
        """empty segments need to be followed by another empty segments \n
        this breaks symmetries in the solution"""
        if segment.previous == None or segment.is_first:
            return pyo.Constraint.Skip
        else:
            # this assumes that minimal fixture width is always >= 1
            return model.widths[segment.previous] * max_fixture_width >= model.widths[segment]

    model.previous_segment_zero = pyo.Constraint(model.segments, rule=previous_segment_zero)

    def no_empty_nonzero_segments(model: KitchenModel, segment: Segment) -> Any:
        """segment has width => it contains a fixture"""
        return model.widths[segment] <= (max_fixture_width * sum(model.pairs[segment, fixture] for fixture in model.fixtures))

    model.no_empty_nonzero_segments = pyo.Constraint(model.segments, rule=no_empty_nonzero_segments)

    def correct_vertical_placement(model: KitchenModel, segment: Segment, fixture: Fixture) -> Any:
        """ensure that the vertical placement of fixtures is correct (in the pair, is_top of the fixture should equal is_top of the segment)"""
        if segment.part.is_top == fixture.is_top:
            return pyo.Constraint.Skip
        else:
            return model.pairs[segment, fixture] == 0

    model.correct_vertical_placement = pyo.Constraint(model.segments, model.fixtures, rule=correct_vertical_placement)

    # WIDTH RULES

    def width_rules(model: KitchenModel, segment: Segment, fixture: Fixture, current_clause: int) -> Any:
        """enforce minimal and maximal fixture width"""
        return get_clause([
            model.widths[segment] >= (fixture.width_min*model.pairs[segment, fixture]),
            model.widths[segment] <= fixture.width_max + max_fixture_width * (1-model.pairs[segment, fixture])
        ], current_clause)

    model.width_rules = pyo.Constraint(model.segments, model.fixtures,
                                       pyo.RangeSet(clause_count := 2), rule=width_rules)

    def part_width(model: KitchenModel, part: KitchenPart) -> Any:
        """total width of the kitchen part should be less then or equal to the sum of the widths of the fixtures"""
        return sum(model.widths[segment] for segment in part.segments) <= part.width

    model.part_width = pyo.Constraint(model.parts, rule=part_width)

    # EDGE RULES

    def edge_fixture(model: KitchenModel, segment: Segment, fixture: Fixture) -> Any:
        """edge segment cannot contain a non-edge fixture"""
        if segment.is_edge and not fixture.allow_edge:
            return model.pairs[segment, fixture] == 0
        else:
            return pyo.Constraint.Skip

    model.edge_fixture = pyo.Constraint(model.segments, model.fixtures, rule=edge_fixture)

    def edge_segment(model: KitchenModel, segment: Segment) -> Any:
        """segment is edge => contains at least one fixture"""
        if segment.is_edge:
            return sum(model.pairs[segment, fixture] for fixture in model.fixtures) >= 1
        else:
            return pyo.Constraint.Skip

    model.edge_segment = pyo.Constraint(model.segments, rule=edge_segment)

    # POSITION RULES

    def get_segments_x(model: KitchenModel, segment: Segment) -> Any:
        """determines x coordinate of the segment"""
        if segment.is_first:
            return model.segments_x[segment] == segment.part.position.x
        else:
            cos_alpha = math.cos(math.radians(segment.part.position.angle))
            return model.segments_x[segment] == model.segments_x[segment.previous] + model.widths[segment.previous] * cos_alpha

    model.get_segments_x = pyo.Constraint(model.segments, rule=get_segments_x)

    def get_segments_y(model: KitchenModel, segment: Segment) -> Any:
        """determines y coordinate of the segment"""
        if segment.is_first:
            return model.segments_y[segment] == segment.part.position.y
        else:
            sin_alpha = math.sin(math.radians(segment.part.position.angle))
            return model.segments_y[segment] == model.segments_y[segment.previous] + model.widths[segment.previous] * sin_alpha

    model.get_segments_y = pyo.Constraint(model.segments, rule=get_segments_y)

    def get_segments_offset(model: KitchenModel, segment: Segment) -> Any:
        """determines offset of the segment relative to the group"""
        if segment.is_first:
            return model.segments_offset[segment] == segment.part.position.group_offset
        else:
            return model.segments_offset[segment] == model.segments_offset[segment.previous] + model.widths[segment.previous]

    model.get_segments_offset = pyo.Constraint(model.segments, rule=get_segments_offset)

    def get_fixtures_width_position(model: KitchenModel, segment: Segment, fixture: Fixture, current_clause: int) -> Any:
        """propagates width, coordinates and group info from segments to their assigned fixtures \n
        absent fixtures should have only zeroes (except for coordinates)"""
        MW = max_fixture_width
        MC = max_canvas_size
        p = model.pairs[segment, fixture]

        sw = model.widths[segment]
        fw = model.fixtures_width[fixture]
        sx = model.segments_x[segment]
        fx = model.fixtures_x[fixture]
        sy = model.segments_y[segment]
        fy = model.fixtures_y[fixture]
        so = model.segments_offset[segment]
        fo = model.fixtures_offset[fixture]
        sg = segment.part.position.group_number
        fg = model.fixtures_group[fixture]

        clauses = [
            sw-MW*(1-p) <= fw,  # lower bound
            fw <= sw+MW*(1-p),  # upper bound
            fw <= MW*model.present[fixture],  # zero if absent

            sx-MC*(1-p) <= fx,
            fx <= sx+MC*(1-p),

            sy-MC*(1-p) <= fy,
            fy <= sy+MC*(1-p),

            so-MC*(1-p) <= fo,
            fo <= so+MC*(1-p),
            fo <= MC*model.present[fixture],

            sg-MC*(1-p) <= fg,
            fg <= sg+MC*(1-p),
            fg <= MC*model.present[fixture]
        ]
        return get_clause(clauses, current_clause)

    model.get_fixtures_width_coords_offset = pyo.Constraint(
        model.segments, model.fixtures, pyo.RangeSet(clause_count := 13), rule=get_fixtures_width_position)

    def preserve_tall_fixtures(model: KitchenModel, fixture: Fixture, current_clause: int) -> Any:
        """ensures that tall fixtures (with top and bottom part) are not split in half"""
        if fixture.complementary_fixture is not None:
            return get_clause([
                model.fixtures_offset[fixture] <= model.fixtures_offset[fixture.complementary_fixture],
                model.fixtures_group[fixture] <= model.fixtures_group[fixture.complementary_fixture],
                model.fixtures_width[fixture] <= model.fixtures_width[fixture.complementary_fixture]
            ], current_clause)
        else:
            return pyo.Constraint.Skip

    model.preserve_tall_fixtures = pyo.Constraint(
        model.fixtures, pyo.RangeSet(clause_count := 3), rule=preserve_tall_fixtures)

    # BAN/REQUIRE RULES

    # TODO: ban fixture from specific place (using group), require certain fixture type,
    # get difference from previous width for each segment, add *right* edge segments,
    # FIXME: break symmetries for allow_multiple

    """
    • ban fixtures in group
    • ban fixtures in group part
    • require one or more fixtures in kitchen
    • require one or more fixtures in group
    • require one or more fixtures in group part
    """


def set_objective(model: KitchenModel) -> None:
    def fitness(model: KitchenModel) -> Any:
        # prefer more present fixtures
        present_count = sum(model.present[fixture] for fixture in model.fixtures)
        # prefer greater total width
        width_coeff = sum(model.widths[segment] for segment in model.segments) / 10
        return present_count + width_coeff

    model.fitness = pyo.Objective(rule=fitness, sense=pyo.maximize)


def find_model(model: KitchenModel) -> None:
    opt = pyo.SolverFactory('glpk')
    # opt = pyo.SolverFactory('gurobi_direct')
    result_obj = opt.solve(model, tee=True)
    model.pprint()


def save_result(kitchen: Kitchen, model: KitchenModel) -> None:
    for segment in kitchen.segments:
        segment.width = pyo.value(model.widths[segment], exception=False)

        if segment.width is None:
            segment.width = 0

        for fixture in kitchen.fixtures:
            if pyo.value(model.pairs[segment, fixture], exception=False):
                segment.fixture = fixture
