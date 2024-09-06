from kitchen import *
from typing import Any

def attr_matches(rule: PlacementRule, fixture: Fixture) -> Any:
    """check if the fixture is affected by the rule"""
    return getattr(fixture, rule.attribute_name) == rule.attribute_value
