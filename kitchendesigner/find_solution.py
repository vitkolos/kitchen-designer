from kitchen import Kitchen, Segment, Fixture
from typing import Any
import random
import pyomo.environ as pyo


def solve(kitchen: Kitchen) -> None:
    model = pyo.ConcreteModel()
    create_variables(kitchen, model)
    set_constraints(kitchen, model)
    set_objective(kitchen, model)
    find_model(model)
    save_result(kitchen, model)


def create_variables(kitchen: Kitchen, model: pyo.Model) -> None:
    max_item_width = 100

    model.present = pyo.Var(kitchen.fixtures, within=pyo.Binary)
    model.widths = pyo.Var(kitchen.segments, bounds=(0, max_item_width))
    model.pairs = pyo.Var(kitchen.segments, kitchen.fixtures, within=pyo.Binary)


def set_constraints(kitchen: Kitchen, model: pyo.Model) -> None:
    def presencePairsPairing(model: pyo.Model, fixture: Fixture) -> Any:
        return sum(model.pairs[segment, fixture] for segment in kitchen.segments) == model.present[fixture]

    def minItemWidth(model: pyo.Model, segment: Segment, fixture: Fixture) -> Any:
        return model.widths[segment] >= (fixture.width_min*model.pairs[segment, fixture])

    model.presencePairsPairing = pyo.Constraint(kitchen.fixtures, rule=presencePairsPairing)
    model.minItemWidth = pyo.Constraint(kitchen.segments, kitchen.fixtures, rule=minItemWidth)


def set_objective(kitchen: Kitchen, model: pyo.Model) -> None:
    model.fitness = pyo.Objective(rule=lambda model: sum(
        model.present[fixture] for fixture in kitchen.fixtures), sense=pyo.maximize)


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
