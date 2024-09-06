import json
import jsonschema
import pathlib
import math
import dataclasses
from kitchen import *
from typing import Any
from utility_functions import attr_matches


def load(file_name: str) -> Kitchen:
    loaded_data = load_data_from_files(file_name)
    zones = load_zones(loaded_data['zones'])
    fixtures = load_fixtures(loaded_data['available_fixtures'], [zone.name for zone in zones])
    constants = load_constants(loaded_data['constants'])
    parts, segments = load_parts_segments(loaded_data['kitchen_parts'], constants)
    walls = load_walls(get_list_field(loaded_data, 'walls'))
    corners = load_corners(get_list_field(loaded_data, 'corners'), parts)
    placement_rules = load_placement_rules(get_list_field(loaded_data, 'placement_rules'))
    relation_rules = load_relation_rules(get_list_field(loaded_data, 'relation_rules'))
    remove_fixtures(fixtures, placement_rules, corners)
    groups = list(set(part.position.group_number for part in parts))
    return Kitchen(groups, parts, segments, walls, corners, placement_rules, relation_rules, constants, zones, fixtures)


def get_list_field(data_dict: dict[str, list[dict[str, Any]]], key: str) -> list[dict[str, Any]]:
    """helper function, default for list field is [] (if not present in JSON)"""
    if key in data_dict:
        return data_dict[key]
    else:
        return []


def get_bool_field(data_dict: dict[str, Any], key: str) -> Any:
    """helper function, default for bool field is false (if not present in JSON)"""
    if key in data_dict:
        return data_dict[key]
    else:
        return False


def load_data_from_files(file_name: str) -> Any:
    with open(pathlib.Path(__file__).parent / 'input.schema.json') as schema_file:
        schema = json.load(schema_file)

    with open(file_name) as data_file:
        # raises an exception if json is not valid
        loaded_data = json.load(data_file)

    # raises an exception if validation fails
    jsonschema.validate(instance=loaded_data, schema=schema)
    return loaded_data


def load_zones(zones_data: list[dict[str, Any]]) -> list[Zone]:
    zones = []

    for zone_data in zones_data:
        optimal_center = ((zone_data['optimal_center']['x'], zone_data['optimal_center']['y'])
                          if get_bool_field(zone_data, 'has_optimal_center') else None)
        color = zone_data['color'] if 'color' in zone_data else ''
        zone = Zone(zone_data['name'], get_bool_field(zone_data, 'is_optimized'), optimal_center, color)
        zones.append(zone)

    return zones

def load_constants(constants_data: dict[str, float]) -> Constants:
    constants = Constants()
    constants.min_fixture_width = constants_data['min_fixture_width']
    constants.max_fixture_width = constants_data['max_fixture_width']
    constants.max_canvas_size = constants_data['max_canvas_size']
    constants.vertical_continuity_tolerance = constants_data['vertical_continuity_tolerance']
    constants.width_same_tolerance = constants_data['width_same_tolerance']
    constants.width_different_tolerance = constants_data['width_different_tolerance']
    constants.width_penult_similar_tolerance = constants_data['width_penult_similar_tolerance']
    return constants

def load_fixtures(available_fixtures_data: list[dict[str, Any]], zones_str: list[str]) -> list[Fixture]:
    fixtures = []
    MULTIPLE_FIXTURE_COPY_COUNT = 3

    for fixture_data in available_fixtures_data:
        position_top = get_bool_field(fixture_data, 'position_top')
        position_bottom = get_bool_field(fixture_data, 'position_bottom')
        allow_multiple = get_bool_field(fixture_data, 'allow_multiple')
        is_corner = get_bool_field(fixture_data, 'is_corner')
        zone = fixture_data['zone']
        storage = fixture_data['storage'] if 'storage' in fixture_data else 0
        width_min = fixture_data['width_min']
        width_max = fixture_data['width_max']
        width_min2 = fixture_data['width_min2'] if 'width_min2' in fixture_data else width_min
        width_max2 = fixture_data['width_max2'] if 'width_max2' in fixture_data else width_max
        tall = position_top and position_bottom
        fixture_copy_count = MULTIPLE_FIXTURE_COPY_COUNT if allow_multiple else 1
        previous_fixture_top: Fixture | None
        previous_fixture_bottom: Fixture | None

        if zone not in zones_str:
            raise Exception(f'zone "{zone}" was not defined')

        if not position_top and not position_bottom:
            continue

        for i in range(fixture_copy_count):
            kitchen_fixture_top = Fixture(fixture_data['name'], fixture_data['type'], zone, width_min, width_max,
                                          position_top, storage, get_bool_field(fixture_data, 'has_worktop'), get_bool_field(fixture_data, 'allow_edge'), is_corner)
            kitchen_fixture_bottom = dataclasses.replace(kitchen_fixture_top, is_top=False)

            if i > 0:
                kitchen_fixture_top.name += f'_{i}'
                kitchen_fixture_bottom.name += f'_{i}'
                kitchen_fixture_top.older_sibling = None if tall else previous_fixture_top
                kitchen_fixture_bottom.older_sibling = previous_fixture_bottom

            if tall:
                kitchen_fixture_top.name += 'T'
                kitchen_fixture_bottom.name += 'B'
                kitchen_fixture_top.complementary_fixture = kitchen_fixture_bottom
                kitchen_fixture_bottom.complementary_fixture = kitchen_fixture_top
                kitchen_fixture_top.storage = 0

            previous_fixture_top = kitchen_fixture_top
            previous_fixture_bottom = kitchen_fixture_bottom

            def corner_copy(fixture: Fixture) -> Fixture:
                copy = dataclasses.replace(fixture, name=kitchen_fixture_bottom.name+'+',
                                           width_min=width_min2, width_max=width_max2)
                fixture.second_corner_fixture = copy
                return copy

            if position_top:
                fixtures.append(kitchen_fixture_top)

                if is_corner:
                    fixtures.append(corner_copy(kitchen_fixture_top))

            if position_bottom:
                fixtures.append(kitchen_fixture_bottom)

                if is_corner:
                    fixtures.append(corner_copy(kitchen_fixture_bottom))

    return fixtures


def load_parts_segments(kitchen_parts_data: list[dict[str, Any]], constants: Constants) -> tuple[list[KitchenPart], list[Segment]]:
    segment: Segment | None = None
    previous_segment: Segment | None = None

    parts = []
    kitchen_segments = []
    segment_number = 1

    for part_data in kitchen_parts_data:
        width: float = part_data['width']
        is_top: bool = get_bool_field(part_data, 'is_top')
        edge_left: bool = get_bool_field(part_data, 'edge_left')
        edge_right: bool = get_bool_field(part_data, 'edge_right')
        segment_count = math.ceil(width/constants.min_fixture_width)
        part_segments: list[Segment] = []
        # TODO: 1) check that the entire kitchen can fit in positive coordinates
        #       2) check that group numbers are integers
        position = Position(part_data['position']['x'], part_data['position']['y'],
                            part_data['position']['angle'], part_data['position']['group_number'], part_data['position']['group_offset'])
        kitchen_part = KitchenPart(part_data['name'], is_top, position, width,
                                   part_data['depth'], edge_left, edge_right, part_segments)
        parts.append(kitchen_part)

        for i in range(segment_count):
            segment = Segment(segment_number, kitchen_part, 0, None, i == 0, i == segment_count - 1, previous_segment)

            if previous_segment is not None:
                previous_segment.next = segment

            previous_segment = segment
            segment_number += 1
            part_segments.append(segment)
            kitchen_segments.append(segment)

    constants.max_segment_count = segment_number
    return parts, kitchen_segments


def load_walls(walls_data: list[dict[str, Any]]) -> dict[int, Wall]:
    walls = {}

    for wall_data in walls_data:
        group = wall_data['group']
        walls[group] = Wall(group, wall_data['left'], wall_data['right'])

    return walls


def load_corners(corners_data: list[dict[str, Any]], kitchen_parts: list[KitchenPart]) -> list[Corner]:
    # might raise exceptions if input is not correct
    corners = []

    for corner_data in corners_data:
        part1 = next(p for p in kitchen_parts if p.name == corner_data['part1_name'])
        part2 = next(p for p in kitchen_parts if p.name == corner_data['part2_name'])
        corner = Corner(part1, corner_data['part1_left'], part2, corner_data['part2_left'])
        corners.append(corner)

    return corners


def load_placement_rules(rules_data: list[dict[str, Any]]) -> list[PlacementRule]:
    # might raise exceptions if input is not correct
    rules = []

    for rule_data in rules_data:
        rule = PlacementRule(rule_data['rule_type'], rule_data['area'],
                             rule_data['attribute_name'], rule_data['attribute_value'])

        if rule.area == 'group':
            rule.group = rule_data['group']
        elif rule.area == 'group_section':
            rule.group = rule_data['group']
            rule.section_offset = rule_data['section_offset']
            rule.section_width = rule_data['section_width']

        rules.append(rule)

    return rules


def load_relation_rules(rules_data: list[dict[str, Any]]) -> RelationRules:
    # might raise exceptions if input is not correct
    relation_rules = RelationRules({}, {}, {}, {}, {})

    for rule_data in rules_data:
        rule_type = rule_data['rule_type']
        fixture_type = rule_data['fixture_type']

        match rule_type:
            case 'target':
                relation_rules.targets[fixture_type] = (rule_data['x'], rule_data['y'])
            case 'min_distance':
                fixture_type2 = rule_data['fixture_type2']
                relation_rules.min_distances[(fixture_type, fixture_type2)] = rule_data['length']
            case 'wall_distance':
                relation_rules.wall_distances[fixture_type] = rule_data['length']
            case 'min_worktop':
                relation_rules.min_worktops[fixture_type] = rule_data['length']
            case 'one_wide':
                relation_rules.one_wide[fixture_type] = rule_data['length']

    return relation_rules


def remove_fixtures(fixtures: list[Fixture], rules: list[PlacementRule], corners: list[Corner]) -> None:
    for rule in rules:
        if rule.type == 'exclude' and rule.area == 'kitchen':
            fixtures[:] = [fixture for fixture in fixtures if not attr_matches(rule, fixture)]

    rules[:] = [rule for rule in rules if rule.type != 'exclude' or rule.area != 'kitchen']

    if len(corners) == 0:
        fixtures[:] = [fixture for fixture in fixtures if not fixture.is_corner]
