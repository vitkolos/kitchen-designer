from typing import Any, Iterator
import pyomo.environ as pyo
from pyomo.core.base.var import VarData
from process_args import Args


def print_structure(model: pyo.Model, args: Args) -> None:
    if not args.structure:
        return

    for component in model.component_objects():
        if isinstance(component, pyo.Set):
            continue

        name = component.name
        var_names = get_var_names(component)
        print(name, component.ctype.__name__, ','.join(var_names))


def get_indices(component: Any) -> list[str]:
    return [s.name for s in component.index_set().subsets()]


def get_var_names(component: pyo.Component) -> list[str]:
    return list(set(list(gen_var_names_component(component))))


def gen_var_names_component(component: pyo.Component) -> Iterator[str]:
    for data in component._data.values():
        if isinstance(component, pyo.Constraint):
            yield from gen_var_names_expression(data.body)
        if isinstance(component, pyo.Objective):
            yield from gen_var_names_expression(data.expr)


def gen_var_names_expression(expression: Any) -> Iterator[str]:
    if isinstance(expression, VarData):
        yield expression._component().name
    elif hasattr(expression, 'args'):
        for item in expression.args:
            yield from gen_var_names_expression(item)
