import json
import jsonschema
from kitchen import Kitchen, KitchenPart, Fixture, Segment
from typing import Dict, Any


def load() -> Kitchen:
    schema = {
        "type": "object",
        "properties": {
            "kitchen_shape": {
                "type": "object",
                "properties": {
                    "width": {"type": "number"}
                },
                "required": ["width"]
            },
            "available_fixtures": {
                "type": "array",
                "fixtures": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "type": {"type": "string"},
                        "zone": {"type": "string"},
                        "position_top": {"type": "boolean"},
                        "position_bottom": {"type": "boolean"},
                        "width_min": {"type": "number"},
                        "width_max": {"type": "number"},
                        "has_worktop": {"type": "boolean"},
                        "allow_edge": {"type": "boolean"},
                    },
                    "required": ["name", "width_min"]
                }
            }
        },
        "required": ["kitchen_shape", "available_fixtures"]
    }

    with open('input.json') as f:
        # raises an exception if json is not valid
        loaded_data = json.load(f)

    # raises an exception if validation fails
    jsonschema.validate(instance=loaded_data, schema=schema)

    fixtures = []

    def create_kitchen_fixture(fixture: Dict[str, Any], is_top: bool) -> Fixture:
        return Fixture(fixture['name'], fixture['type'], fixture['zone'], fixture['width_min'], fixture['width_max'], is_top, fixture['has_worktop'], fixture['allow_edge'])

    for fixture in loaded_data['available_fixtures']:
        if fixture['position_top']:
            kitchen_fixture_top = create_kitchen_fixture(fixture, is_top=True)
            fixtures.append(kitchen_fixture_top)
        if fixture['position_bottom']:
            kitchen_fixture_bottom = create_kitchen_fixture(fixture, is_top=False)
            fixtures.append(kitchen_fixture_bottom)
        if fixture['position_top'] and fixture['position_bottom']:
            kitchen_fixture_top.name += 'T'
            kitchen_fixture_bottom.name += 'B'
            kitchen_fixture_top.complementary_fixture = kitchen_fixture_bottom
            kitchen_fixture_bottom.complementary_fixture = kitchen_fixture_top

    width: float = loaded_data['kitchen_shape']['width']
    segment_count = range(int(width)//10)
    segments = []
    segment: Segment | None = None

    for i in segment_count:
        segment = Segment(i, 0, None, i == 0, i == 0, False, segment)
        segments.append(segment)

    parts = [KitchenPart('part1', width, 10, segments)]
    kitchen = Kitchen(parts, segments, fixtures)

    return kitchen
