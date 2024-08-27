from kitchen import Kitchen, Segment, Fixture, KitchenPart
from typing import Any
import pyomo.environ as pyo


def solve(kitchen: Kitchen) -> None:
    model = pyo.ConcreteModel()
    create_sets(kitchen, model)
    create_variables(model)
    set_constraints(model)
    set_objective(model)
    find_model(model)
    save_result(kitchen, model)


def create_sets(kitchen: Kitchen, model: pyo.Model) -> None:
    model.fixtures = pyo.Set(initialize=kitchen.fixtures)
    model.segments = pyo.Set(initialize=kitchen.segments)
    model.parts = pyo.Set(initialize=kitchen.parts)


def create_variables(model: pyo.Model) -> None:
    max_fixture_width = 100

    model.present = pyo.Var(model.fixtures, within=pyo.Binary)
    model.widths = pyo.Var(model.segments, bounds=(0, max_fixture_width))
    model.pairs = pyo.Var(model.segments, model.fixtures, within=pyo.Binary)

    model.width_min = pyo.Param(model.fixtures, initialize=lambda model, fixture: fixture.width_min, mutable=True)


def set_constraints(model: pyo.Model) -> None:
    max_fixture_width = 100

    # BASIC RULES

    def presence_pairs_pairing(model: pyo.Model, fixture: Fixture) -> Any:
        """fixture is present <=> it belongs to exactly one pair \n
        fixture is not present <=> it does not belong to any pair"""
        return model.present[fixture] == sum(model.pairs[segment, fixture] for segment in model.segments)

    model.presence_pairs_pairing = pyo.Constraint(model.fixtures, rule=presence_pairs_pairing)

    def segment_capacity(model: pyo.Model, segment: Segment) -> Any:
        """each segment can contain at most one fixture"""
        return sum(model.pairs[segment, fixture] for fixture in model.fixtures) <= 1

    model.segment_capacity = pyo.Constraint(model.segments, rule=segment_capacity)

    def previous_segment_zero(model: pyo.Model, segment: Segment) -> Any:
        """empty segments need to be followed by another empty segments \n
        this breaks symmetries in the solution"""
        if segment.previous == None or segment.is_first:
            return pyo.Constraint.Skip
        else:
            # this assumes that minimal fixture width is always >= 1
            return model.widths[segment.previous] * max_fixture_width >= model.widths[segment]

    model.previous_segment_zero = pyo.Constraint(model.segments, rule=previous_segment_zero)

    def no_empty_nonzero_segments(model: pyo.Model, segment: Segment) -> Any:
        """segment has width => it contains a fixture"""
        return model.widths[segment] <= (max_fixture_width * sum(model.pairs[segment, fixture] for fixture in model.fixtures))

    model.no_empty_nonzero_segments = pyo.Constraint(model.segments, rule=no_empty_nonzero_segments)

    def correct_vertical_placement(model: pyo.Model, segment: Segment, fixture: Fixture) -> Any:
        """ensure that the vertical placement of fixtures is correct (in the pair, is_top of the fixture should equal is_top of the segment)"""
        if segment.is_top == fixture.is_top:
            return pyo.Constraint.Skip
        else:
            return model.pairs[segment, fixture] == 0

    model.correct_vertical_placement = pyo.Constraint(model.segments, model.fixtures, rule=correct_vertical_placement)

    # WIDTH RULES

    def min_width_rule(model: pyo.Model, segment: Segment, fixture: Fixture) -> Any:
        """minimal fixture width"""
        return model.widths[segment] >= (fixture.width_min*model.pairs[segment, fixture])

    model.min_width_rule = pyo.Constraint(model.segments, model.fixtures, rule=min_width_rule)

    def max_width_rule(model: pyo.Model, segment: Segment, fixture: Fixture) -> Any:
        """maximal fixture width"""
        return model.widths[segment] <= fixture.width_max + max_fixture_width * (1-model.pairs[segment, fixture])

    model.max_width_rule = pyo.Constraint(model.segments, model.fixtures, rule=max_width_rule)

    def part_width(model: pyo.Model, part: KitchenPart) -> Any:
        """total width of the kitchen part should be equal to the sum of the widths of the fixtures"""
        return sum(model.widths[segment] for segment in part.segments) == part.width

    model.part_width = pyo.Constraint(model.parts, rule=part_width)

    # EDGE RULES

    def edge_fixture(model: pyo.Model, segment: Segment, fixture: Fixture) -> Any:
        """segment is edge & contains a fixture => fixture is edge"""
        return int(segment.is_edge)*model.pairs[segment, fixture] <= int(fixture.allow_edge)

    model.edge_fixture = pyo.Constraint(model.segments, model.fixtures, rule=edge_fixture)

    def edge_segment(model: pyo.Model, segment: Segment) -> Any:
        """segment is edge => contains at least one fixture"""
        return int(segment.is_edge) <= sum(model.pairs[segment, fixture] for fixture in model.fixtures)

    model.edge_segment = pyo.Constraint(model.segments, rule=edge_segment)


def set_objective(model: pyo.Model) -> None:
    model.fitness = pyo.Objective(rule=lambda model: sum(
        model.present[fixture] for fixture in model.fixtures), sense=pyo.maximize)


def find_model(model: pyo.Model) -> None:
    opt = pyo.SolverFactory('glpk')
    # opt = pyo.SolverFactory('gurobi_direct')
    result_obj = opt.solve(model, tee=True)
    model.pprint()


def save_result(kitchen: Kitchen, model: pyo.Model) -> None:
    for segment in kitchen.segments:
        segment.width = pyo.value(model.widths[segment])

        for fixture in kitchen.fixtures:
            if pyo.value(model.pairs[segment, fixture]):
                segment.fixture = fixture
