import json
import jsonschema
import pathlib
import math
from kitchen import *
from typing import Dict, Any, List


def load() -> Kitchen:
    loaded_data = load_data_from_files()
    fixtures = load_fictures(loaded_data['available_fixtures'])
    parts, kitchen_segments = load_parts_segments(loaded_data['kitchen_parts'])
    return Kitchen(parts, kitchen_segments, fixtures)


def get_bool_field(fixture: Dict[str, Any], key: str) -> Any:
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


def load_fictures(available_fixtures_data: List[Dict[str, Any]]) -> List[Fixture]:
    fixtures = []
    multiple_fixture_copy_count = 2  # fixme: break symmetries

    def create_kitchen_fixture(fixture_data: Dict[str, Any], is_top: bool) -> Fixture:
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


def load_parts_segments(kitchen_parts_data: List[Dict[str, Any]]) -> tuple[List[KitchenPart], List[Segment]]:
    units_per_segment = 10
    segment: Segment | None = None

    parts = []
    kitchen_segments = []
    segment_number = 0

    for part_data in kitchen_parts_data:
        width: float = part_data['width']
        is_top: bool = get_bool_field(part_data, 'is_top')
        segment_count = math.ceil(width/units_per_segment)
        part_segments: List[Segment] = []
        position = Position(part_data['position']['x'], part_data['position']['y'], part_data['position']['angle'])
        kitchen_part = KitchenPart(part_data['name'], is_top, position, width, part_data['depth'], part_segments)
        parts.append(kitchen_part)

        for i in range(segment_count):
            segment = Segment(segment_number, kitchen_part, 0, None, i == 0, i == 0, segment)
            segment_number += 1
            part_segments.append(segment)
            kitchen_segments.append(segment)

    return parts, kitchen_segments
