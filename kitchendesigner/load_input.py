import json
import jsonschema
import pathlib
import math
from kitchen import *
from typing import Any


def load() -> Kitchen:
    loaded_data = load_data_from_files()
    fixtures = load_fictures(loaded_data['available_fixtures'])
    parts, kitchen_segments = load_parts_segments(loaded_data['kitchen_parts'])
    rules = load_rules(loaded_data['rules'])
    preprocess_fixtures_and_rules(fixtures, rules)
    groups = list(set(part.position.group_number for part in parts))
    return Kitchen(groups, parts, kitchen_segments, rules, fixtures)


def get_bool_field(fixture: dict[str, Any], key: str) -> Any:
    """helper function, default for bool field is false (if not present in JSON)"""
    if key in fixture:
        return fixture[key]
    else:
        return False


def load_data_from_files() -> Any:
    with open(pathlib.Path(__file__).parent / 'input.schema.json') as schema_file:
        schema = json.load(schema_file)

    with open('input.json') as data_file:
        # raises an exception if json is not valid
        loaded_data = json.load(data_file)

    # raises an exception if validation fails
    jsonschema.validate(instance=loaded_data, schema=schema)
    return loaded_data


def load_fictures(available_fixtures_data: list[dict[str, Any]]) -> list[Fixture]:
    fixtures = []
    multiple_fixture_copy_count = 2  # FIXME: break symmetries

    def create_kitchen_fixture(fixture_data: dict[str, Any], is_top: bool) -> Fixture:
        fixture = Fixture(fixture_data['name'], fixture_data['type'], fixture_data['zone'], fixture_data['width_min'],
                          fixture_data['width_max'], is_top, get_bool_field(fixture_data, 'has_worktop'), get_bool_field(fixture_data, 'allow_edge'))
        return fixture

    for fixture_data in available_fixtures_data:
        fixture_copy_count = 1
        position_top = get_bool_field(fixture_data, 'position_top')
        position_bottom = get_bool_field(fixture_data, 'position_bottom')

        if get_bool_field(fixture_data, 'allow_multiple'):
            fixture_copy_count = multiple_fixture_copy_count

        for i in range(fixture_copy_count):
            if position_top:
                kitchen_fixture_top = create_kitchen_fixture(fixture_data, is_top=True)
                fixtures.append(kitchen_fixture_top)

                if i > 0:
                    kitchen_fixture_top.name += f'_{i}'

            if position_bottom:
                kitchen_fixture_bottom = create_kitchen_fixture(fixture_data, is_top=False)
                fixtures.append(kitchen_fixture_bottom)

                if i > 0:
                    kitchen_fixture_bottom.name += f'_{i}'

            if position_top and position_bottom:
                kitchen_fixture_top.name += 'T'
                kitchen_fixture_bottom.name += 'B'
                kitchen_fixture_top.complementary_fixture = kitchen_fixture_bottom
                kitchen_fixture_bottom.complementary_fixture = kitchen_fixture_top

    return fixtures


def load_parts_segments(kitchen_parts_data: list[dict[str, Any]]) -> tuple[list[KitchenPart], list[Segment]]:
    units_per_segment = 10
    segment: Segment | None = None

    parts = []
    kitchen_segments = []
    segment_number = 0

    for part_data in kitchen_parts_data:
        width: float = part_data['width']
        is_top: bool = get_bool_field(part_data, 'is_top')
        segment_count = math.ceil(width/units_per_segment)
        part_segments: list[Segment] = []
        position = Position(part_data['position']['x'], part_data['position']['y'],
                            part_data['position']['angle'], part_data['position']['group_number'], part_data['position']['group_offset'])
        kitchen_part = KitchenPart(part_data['name'], is_top, position, width, part_data['depth'], part_segments)
        parts.append(kitchen_part)

        for i in range(segment_count):
            segment = Segment(segment_number, kitchen_part, 0, None, i == 0, i == 0, segment)
            segment_number += 1
            part_segments.append(segment)
            kitchen_segments.append(segment)

    return parts, kitchen_segments


def load_rules(rules_data: list[dict[str, Any]]) -> list[Rule]:
    # raises exceptions if input JSON is invalid
    rules = []

    for rule_data in rules_data:
        rule = Rule(rule_data['type'], rule_data['area'], rule_data['attribute_name'], rule_data['attribute_value'])

        if rule.area == 'group':
            rule.group = rule_data['group']
        elif rule.area == 'group_section':
            rule.group = rule_data['group']
            rule.section_offset = rule_data['section_offset']
            rule.section_width = rule_data['section_width']

        rules.append(rule)

    return rules


def preprocess_fixtures_and_rules(fixtures: list[Fixture], rules: list[Rule]) -> None:
    for rule in rules:
        if rule.type == 'exclude' and rule.area == 'kitchen':
            fixtures[:] = [fixture for fixture in fixtures if
                           getattr(fixture, rule.attribute_name) != rule.attribute_value]

    rules[:] = [rule for rule in rules if rule.type != 'exclude' or rule.area != 'kitchen']
