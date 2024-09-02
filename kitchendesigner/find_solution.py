from kitchen import *
from typing import Any
import pyomo.environ as pyo
import math

min_fixture_width = 10
max_fixture_width = 100
max_canvas_size = 800
max_segment_count = 100
vertical_continuity_tolerance = 0.1
width_same_tolerance = 1
width_different_tolerance = 5
width_penult_similar_tolerance = 2


def solve(kitchen: Kitchen) -> None:
    model = KitchenModel(kitchen)
    set_constraints(kitchen, model)
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
        model.groups = pyo.Set(initialize=kitchen.groups)
        model.rules_all = pyo.Set(initialize=kitchen.rules)
        model.rules_section = pyo.Set(initialize=model.rules_all, filter=lambda _, rule: rule.area == 'group_section')
        model.zones = pyo.Set(initialize=[zone.name for zone in kitchen.zones if zone.is_optimized])

        # product variables
        model.pairs = pyo.Var(model.segments, model.fixtures, domain=pyo.Binary)
        model.present_groups = pyo.Var(model.groups, model.fixtures, domain=pyo.Binary)
        model.rules_section_bin = pyo.Var(model.rules_section, model.fixtures, domain=pyo.Binary)
        model.segment_begins_before = pyo.Var(model.segments, model.segments, domain=pyo.Binary, initialize=0)
        model.segment_ends_after = pyo.Var(model.segments, model.segments, domain=pyo.Binary, initialize=0)
        model.segment_intersects = pyo.Var(model.segments, model.segments, domain=pyo.Binary, initialize=0)
        model.part_segment_begins_before = pyo.Var(model.parts, model.segments, domain=pyo.Binary, initialize=0)
        model.part_segment_ends_after = pyo.Var(model.parts, model.segments, domain=pyo.Binary, initialize=0)
        model.part_segment_intersects = pyo.Var(model.parts, model.segments, domain=pyo.Binary, initialize=0)

        # segment variables
        model.widths = pyo.Var(model.segments, domain=pyo.NonNegativeReals, bounds=(0, max_fixture_width))
        model.used = pyo.Var(model.segments, domain=pyo.Binary)
        model.segments_x = pyo.Var(model.segments, domain=pyo.NonNegativeReals, bounds=(0, max_canvas_size))
        model.segments_y = pyo.Var(model.segments, domain=pyo.NonNegativeReals, bounds=(0, max_canvas_size))
        model.segments_offset = pyo.Var(model.segments, domain=pyo.NonNegativeReals, bounds=(0, max_canvas_size))
        model.segments_width_difference = pyo.Var(
            model.segments, domain=pyo.NonNegativeReals, bounds=(0, max_fixture_width))
        model.segments_previous_larger = pyo.Var(model.segments, domain=pyo.Binary)
        model.segments_width_not_same = pyo.Var(model.segments, domain=pyo.Binary)
        model.segments_width_really_different = pyo.Var(model.segments, domain=pyo.Binary)
        model.segments_penult_width_difference = pyo.Var(
            model.segments, domain=pyo.NonNegativeReals, bounds=(0, max_fixture_width))
        model.segments_penult_previous_larger = pyo.Var(model.segments, domain=pyo.Binary)
        model.segments_penult_similar = pyo.Var(model.segments, domain=pyo.Binary)
        model.segments_pattern_aba = pyo.Var(model.segments, domain=pyo.Binary)

        # fixture variables
        model.present = pyo.Var(model.fixtures, domain=pyo.Binary)
        model.fixtures_x = pyo.Var(model.fixtures, domain=pyo.NonNegativeReals, bounds=(0, max_canvas_size))
        model.fixtures_y = pyo.Var(model.fixtures, domain=pyo.NonNegativeReals, bounds=(0, max_canvas_size))
        model.fixtures_width = pyo.Var(model.fixtures, domain=pyo.NonNegativeReals, bounds=(0, max_fixture_width))
        model.fixtures_offset = pyo.Var(model.fixtures, domain=pyo.NonNegativeReals, bounds=(0, max_canvas_size))
        model.fixtures_segment_number = pyo.Var(
            model.fixtures, domain=pyo.NonNegativeIntegers, bounds=(0, max_segment_count))
        model.zones_x_helper = pyo.Var(model.fixtures, domain=pyo.NonNegativeReals, bounds=(0, max_canvas_size))
        model.zones_y_helper = pyo.Var(model.fixtures, domain=pyo.NonNegativeReals, bounds=(0, max_canvas_size))
        model.fixtures_zone_x_dist = pyo.Var(model.fixtures, domain=pyo.NonNegativeReals,
                                             bounds=(0, max_canvas_size), initialize=0)
        model.fixtures_zone_x_further = pyo.Var(model.fixtures, domain=pyo.Binary, initialize=0)
        model.fixtures_zone_y_dist = pyo.Var(model.fixtures, domain=pyo.NonNegativeReals,
                                             bounds=(0, max_canvas_size), initialize=0)
        model.fixtures_zone_y_further = pyo.Var(model.fixtures, domain=pyo.Binary, initialize=0)
        model.fixtures_target_x_dist = pyo.Var(model.fixtures, domain=pyo.NonNegativeReals,
                                               bounds=(0, max_canvas_size), initialize=0)
        model.fixtures_target_x_further = pyo.Var(model.fixtures, domain=pyo.Binary, initialize=0)
        model.fixtures_target_y_dist = pyo.Var(model.fixtures, domain=pyo.NonNegativeReals,
                                               bounds=(0, max_canvas_size), initialize=0)
        model.fixtures_target_y_further = pyo.Var(model.fixtures, domain=pyo.Binary, initialize=0)

        # zone variables
        model.zones_x = pyo.Var(model.zones, domain=pyo.NonNegativeReals, bounds=(0, max_canvas_size))
        model.zones_y = pyo.Var(model.zones, domain=pyo.NonNegativeReals, bounds=(0, max_canvas_size))
        model.zones_x_dist = pyo.Var(model.zones, domain=pyo.NonNegativeReals,
                                     bounds=(0, max_canvas_size), initialize=0)
        model.zones_x_further = pyo.Var(model.zones, domain=pyo.Binary, initialize=0)
        model.zones_y_dist = pyo.Var(model.zones, domain=pyo.NonNegativeReals,
                                     bounds=(0, max_canvas_size), initialize=0)
        model.zones_y_further = pyo.Var(model.zones, domain=pyo.Binary, initialize=0)

        # part variables
        model.parts_padding = pyo.Var(model.parts, domain=pyo.NonNegativeReals,
                                      bounds=(0, max_canvas_size), initialize=0)


def set_constraints(kitchen: Kitchen, model: KitchenModel) -> None:
    clause_count = 0

    def get_clause(clauses: list[Any], current_clause: int) -> Any:
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

    def segment_used(model: KitchenModel, segment: Segment) -> Any:
        """check if segment is used"""
        return model.used[segment] == sum(model.pairs[segment, fixture] for fixture in model.fixtures)

    model.segment_used = pyo.Constraint(model.segments, rule=segment_used)

    def previous_segment_zero(model: KitchenModel, segment: Segment) -> Any:
        """empty segments need to be followed by another empty segments \n
        this breaks symmetries in the solution"""
        if segment.previous is None or segment.is_first:
            return pyo.Constraint.Skip
        else:
            return model.used[segment] <= model.used[segment.previous]

    model.previous_segment_zero = pyo.Constraint(model.segments, rule=previous_segment_zero)

    def no_empty_nonzero_segments(model: KitchenModel, segment: Segment) -> Any:
        """segment has width => it contains a fixture"""
        return model.widths[segment] <= max_fixture_width * model.used[segment]

    model.no_empty_nonzero_segments = pyo.Constraint(model.segments, rule=no_empty_nonzero_segments)

    def no_zero_nonempty_segments(model: KitchenModel, segment: Segment) -> Any:
        """segment contains a fixture => its width is at least minimal"""
        return model.widths[segment] >= min_fixture_width * model.used[segment]

    model.no_zero_nonempty_segments = pyo.Constraint(model.segments, rule=no_zero_nonempty_segments)

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
        """total width of the kitchen part should be less than or equal to the sum of the widths of the fixtures"""
        return model.parts_padding[part] + sum(model.widths[segment] for segment in part.segments) <= part.width

    model.part_width = pyo.Constraint(model.parts, rule=part_width)

    # EDGE RULES

    def edge_fixture(model: KitchenModel, segment: Segment, fixture: Fixture) -> Any:
        """first edge segment cannot contain a non-edge fixture"""
        if segment.is_first and segment.part.edge_left and not fixture.allow_edge:
            return model.pairs[segment, fixture] == 0
        else:
            return pyo.Constraint.Skip

    model.edge_fixture = pyo.Constraint(model.segments, model.fixtures, rule=edge_fixture)

    def edge_fixture_last_segment(model: KitchenModel, segment: Segment, fixture: Fixture) -> Any:
        """last edge segment cannot contain a non-edge fixture"""
        if segment.is_last and segment.part.edge_right and not fixture.allow_edge:
            return model.pairs[segment, fixture] == 0
        else:
            return pyo.Constraint.Skip

    model.edge_fixture_last_segment = pyo.Constraint(model.segments, model.fixtures, rule=edge_fixture_last_segment)

    def edge_fixture_empty_segment(model: KitchenModel, segment: Segment, fixture: Fixture) -> Any:
        """non-edge fixture has to be succeeded by another fixture"""
        if not segment.is_first and segment.part.edge_right and not fixture.allow_edge:
            return model.pairs[segment.previous, fixture] <= model.used[segment]
        else:
            return pyo.Constraint.Skip

    model.edge_fixture_empty_segment = pyo.Constraint(model.segments, model.fixtures, rule=edge_fixture_empty_segment)

    # POSITION RULES

    def get_segments_x(model: KitchenModel, segment: Segment) -> Any:
        """determines x coordinate of the *center* of the segment"""
        sin_alpha = math.sin(math.radians(segment.part.position.angle))
        cos_alpha = math.cos(math.radians(segment.part.position.angle))

        if segment.is_first:
            horizontal = model.parts_padding[segment.part] + model.widths[segment]/2
            vertical = segment.part.depth/2
            return model.segments_x[segment] == segment.part.position.x + horizontal * cos_alpha - vertical * sin_alpha
        else:
            return model.segments_x[segment] == model.segments_x[segment.previous] + (model.widths[segment]/2 + model.widths[segment.previous]/2) * cos_alpha

    model.get_segments_x = pyo.Constraint(model.segments, rule=get_segments_x)

    def get_segments_y(model: KitchenModel, segment: Segment) -> Any:
        """determines y coordinate of the *center* of the segment"""
        sin_alpha = math.sin(math.radians(segment.part.position.angle))
        cos_alpha = math.cos(math.radians(segment.part.position.angle))

        if segment.is_first:
            horizontal = model.parts_padding[segment.part] + model.widths[segment]/2
            vertical = segment.part.depth/2
            return model.segments_y[segment] == segment.part.position.y + horizontal * sin_alpha + vertical * cos_alpha
        else:
            return model.segments_y[segment] == model.segments_y[segment.previous] + (model.widths[segment]/2 + model.widths[segment.previous]/2) * sin_alpha

    model.get_segments_y = pyo.Constraint(model.segments, rule=get_segments_y)

    def get_segments_offset(model: KitchenModel, segment: Segment) -> Any:
        """determines offset of the segment relative to the group"""
        if segment.is_first:
            return model.segments_offset[segment] == segment.part.position.group_offset + model.parts_padding[segment.part]
        else:
            return model.segments_offset[segment] == model.segments_offset[segment.previous] + model.widths[segment.previous]

    model.get_segments_offset = pyo.Constraint(model.segments, rule=get_segments_offset)

    def get_fixtures_width_position(model: KitchenModel, segment: Segment, fixture: Fixture, current_clause: int) -> Any:
        """propagates width and coordinates from segments to their assigned fixtures \n
        absent fixtures should have only zeroes"""
        MW = max_fixture_width
        MC = max_canvas_size
        MN = max_segment_count
        p = model.pairs[segment, fixture]

        sw = model.widths[segment]
        fw = model.fixtures_width[fixture]
        sx = model.segments_x[segment]
        fx = model.fixtures_x[fixture]
        sy = model.segments_y[segment]
        fy = model.fixtures_y[fixture]
        so = model.segments_offset[segment]
        fo = model.fixtures_offset[fixture]
        sn = segment.number
        fn = model.fixtures_segment_number[fixture]

        clauses = [
            # segment width -> fixture width
            sw-MW*(1-p) <= fw,  # lower bound
            fw <= sw+MW*(1-p),  # upper bound
            fw <= MW*model.present[fixture],  # zero if absent

            # segment x -> fixture x
            sx-MC*(1-p) <= fx,
            fx <= sx+MC*(1-p),
            fx <= MC*model.present[fixture],

            # segment y -> fixture y
            sy-MC*(1-p) <= fy,
            fy <= sy+MC*(1-p),
            fy <= MC*model.present[fixture],

            # segment offset -> fixture offset
            so-MC*(1-p) <= fo,
            fo <= so+MC*(1-p),
            fo <= MC*model.present[fixture],

            # segment number -> fixture segment_number
            sn-MN*(1-p) <= fn,
            fn <= sn+MN*(1-p),
            fn <= MN*model.present[fixture],
        ]
        return get_clause(clauses, current_clause)

    model.get_fixtures_width_coords_offset = pyo.Constraint(
        model.segments, model.fixtures, pyo.RangeSet(clause_count := 15), rule=get_fixtures_width_position)

    def get_present_groups(model: KitchenModel, group: int, fixture: Fixture) -> Any:
        """checks if the fixture is present in the group"""
        return sum(model.pairs[segment, fixture] for segment in model.segments if segment.part.position.group_number == group) == model.present_groups[group, fixture]

    model.get_present_groups = pyo.Constraint(model.groups, model.fixtures, rule=get_present_groups)

    # TALL FIXTURES RULES

    def preserve_tall_fixtures_offset_width(model: KitchenModel, fixture: Fixture, current_clause: int) -> Any:
        """ensures that tall fixtures (with top and bottom part) are not split in half"""
        if fixture.complementary_fixture is not None:
            return get_clause([
                model.fixtures_offset[fixture] <= model.fixtures_offset[fixture.complementary_fixture],
                model.fixtures_width[fixture] <= model.fixtures_width[fixture.complementary_fixture]
            ], current_clause)
        else:
            return pyo.Constraint.Skip

    model.preserve_tall_fixtures_offset_width = pyo.Constraint(
        model.fixtures, pyo.RangeSet(clause_count := 2), rule=preserve_tall_fixtures_offset_width)

    def preserve_tall_fixtures_group(model: KitchenModel, group: int, fixture: Fixture) -> Any:
        """ensures that tall fixtures (with top and bottom part) are not split in half"""
        if fixture.complementary_fixture is not None:
            return model.present_groups[group, fixture] <= model.present_groups[group, fixture.complementary_fixture]
        else:
            return pyo.Constraint.Skip

    model.preserve_tall_fixtures_group = pyo.Constraint(model.groups, model.fixtures, rule=preserve_tall_fixtures_group)

    # EXCLUDE/INCLUDE RULES

    def attr_matches(rule: Rule, fixture: Fixture) -> Any:
        """check if the fixture is affected by the rule"""
        return getattr(fixture, rule.attribute_name) == rule.attribute_value

    def evaluate_user_rules(model: KitchenModel, rule: Rule) -> Any:
        """applies some of the user-defined rules"""
        match rule.type:
            case 'include':
                match rule.area:
                    case 'kitchen':
                        return sum(model.present[fixture] for fixture in model.fixtures if attr_matches(rule, fixture)) >= 1
                    case 'group':
                        return sum(model.present_groups[rule.group, fixture] for fixture in model.fixtures if attr_matches(rule, fixture)) >= 1
                    case 'group_section':
                        # this is the first part of the rule (see evaluate_user_rules_section)
                        return sum(model.rules_section_bin[rule, fixture] for fixture in model.fixtures if attr_matches(rule, fixture)) >= 1
            case 'exclude':
                match rule.area:
                    case 'group':
                        return sum(model.present_groups[rule.group, fixture] for fixture in model.fixtures if attr_matches(rule, fixture)) <= 0
                    case 'group_section':
                        return pyo.Constraint.Skip  # the constraints are in evaluate_user_rules_section

    model.evaluate_user_rules = pyo.Constraint(model.rules_all, rule=evaluate_user_rules)

    def evaluate_user_rules_section(model: KitchenModel, rule: Rule, fixture: Fixture, current_clause: int) -> Any:
        """applies the user-defined rules that use sections"""
        if attr_matches(rule, fixture):
            M = max_canvas_size
            b = model.rules_section_bin[rule, fixture]
            correct_group = model.present_groups[rule.group, fixture]

            match rule.type:
                case 'include':
                    # this is the second part of the rule (see evaluate_user_rules)
                    clauses = [
                        correct_group >= b,
                        model.fixtures_offset[fixture] >= rule.section_offset*b,
                        model.fixtures_offset[fixture] + model.fixtures_width[fixture]
                        <= rule.section_offset + rule.section_width + (1-b)*M
                    ]
                case 'exclude':
                    clauses = [
                        model.fixtures_offset[fixture] + model.fixtures_width[fixture]
                        <= rule.section_offset + M*b + M*(1-correct_group),
                        rule.section_offset + rule.section_width
                        <= model.fixtures_offset[fixture] + M*(1-b) + M*(1-correct_group),
                        pyo.Constraint.Skip
                    ]

            return get_clause(clauses, current_clause)
        else:
            return pyo.Constraint.Skip

    model.evaluate_user_rules_section = pyo.Constraint(
        model.rules_section, model.fixtures, pyo.RangeSet(clause_count := 3), rule=evaluate_user_rules_section)

    # WIDTH DIFFERENCE RULES

    def get_width_difference(model: KitchenModel, segment: Segment, current_clause: int) -> Any:
        """detects width differences between neighbouring segments"""
        width_difference = model.segments_width_difference[segment]

        if segment.is_first:
            if current_clause == 1:
                return width_difference <= 0
            else:
                return pyo.Constraint.Skip
        else:
            M = max_fixture_width
            current_width = model.widths[segment]
            previous_width = model.widths[segment.previous]

            clauses = [
                width_difference >= previous_width - current_width - M*(1-model.used[segment]),
                width_difference >= current_width - previous_width - M*(1-model.used[segment]),
                width_difference <= previous_width - current_width + M*(1-model.segments_previous_larger[segment]),
                width_difference <= current_width - previous_width + M*model.segments_previous_larger[segment],
                width_difference <= M*model.used[segment]
            ]
            return get_clause(clauses, current_clause)

    model.get_width_difference = pyo.Constraint(
        model.segments, pyo.RangeSet(clause_count := 5), rule=get_width_difference)

    def get_width_difference_penult(model: KitchenModel, segment: Segment, current_clause: int) -> Any:
        """detects width differences between current and penultimate segment"""
        width_difference = model.segments_penult_width_difference[segment]

        if segment.is_first or segment.previous is None or segment.previous.is_first:
            if current_clause == 1:
                return width_difference <= 0
            else:
                return pyo.Constraint.Skip
        else:
            M = max_fixture_width
            current_width = model.widths[segment]
            previous_width = model.widths[segment.previous.previous]

            clauses = [
                width_difference >= previous_width - current_width - M*(1-model.used[segment]),
                width_difference >= current_width - previous_width - M*(1-model.used[segment]),
                width_difference <= previous_width - current_width + M *
                (1-model.segments_penult_previous_larger[segment]),
                width_difference <= current_width - previous_width + M*model.segments_penult_previous_larger[segment],
                width_difference <= M*model.used[segment]
            ]
            return get_clause(clauses, current_clause)

    model.get_width_difference_penult = pyo.Constraint(
        model.segments, pyo.RangeSet(clause_count := 5), rule=get_width_difference_penult)

    # MULTIPLE SAME FIXTURES RULE

    def sort_multiple_same_fixtures(model: KitchenModel, fixture: Fixture) -> Any:
        """older clones must have lower segment number \n
        this breaks symmetries in the solution"""
        if fixture.older_sibling is not None:
            return model.fixtures_segment_number[fixture.older_sibling] <= model.fixtures_segment_number[fixture]
        else:
            return pyo.Constraint.Skip

    model.sort_multiple_same_fixtures = pyo.Constraint(model.fixtures, rule=sort_multiple_same_fixtures)

    # ZONE RULES

    def get_zone_coordinates_sync(model: KitchenModel, fixture: Fixture, current_clause: int) -> Any:
        """first part of the calculation of the average coordinates of the zone fixtures"""
        zone = fixture.zone

        if zone in model.zones:
            M = max_canvas_size
            x = model.zones_x[zone]
            xf = model.zones_x_helper[fixture]
            y = model.zones_y[zone]
            yf = model.zones_y_helper[fixture]
            pf = model.present[fixture]

            clauses = [
                xf <= pf*M,
                xf >= x-M*(1-pf),
                xf <= x,

                yf <= pf*M,
                yf >= y-M*(1-pf),
                yf <= y
            ]
            return get_clause(clauses, current_clause)
        else:
            return pyo.Constraint.Skip

    model.get_zone_coordinates_sync = pyo.Constraint(
        model.fixtures, pyo.RangeSet(clause_count := 6), rule=get_zone_coordinates_sync)

    def get_zone_coordinates_sums(model: KitchenModel, zone: str, current_clause: int) -> Any:
        """second part of the calculation of the average coordinates of the zone fixtures"""
        clauses = [
            sum(model.zones_x_helper[fixture] for fixture in model.fixtures if fixture.zone == zone)
            == sum(model.fixtures_x[fixture] for fixture in model.fixtures if fixture.zone == zone),
            sum(model.zones_y_helper[fixture] for fixture in model.fixtures if fixture.zone == zone)
            == sum(model.fixtures_y[fixture] for fixture in model.fixtures if fixture.zone == zone),
        ]
        return get_clause(clauses, current_clause)

    model.get_zone_coordinates_sums = pyo.Constraint(
        model.zones, pyo.RangeSet(clause_count := 2), rule=get_zone_coordinates_sums)

    def get_fixture_zone_distance(model: KitchenModel, fixture: Fixture, current_clause: int) -> Any:
        """calculates the distance each fixture has from the zone center"""
        p = model.present[fixture]
        M = max_canvas_size

        x_dist = model.fixtures_zone_x_dist[fixture]
        x_further = model.fixtures_zone_x_further[fixture]
        y_dist = model.fixtures_zone_y_dist[fixture]
        y_further = model.fixtures_zone_y_further[fixture]

        if fixture.zone in model.zones:
            fixture_x = model.fixtures_x[fixture]
            zone_x = model.zones_x[fixture.zone]
            fixture_y = model.fixtures_y[fixture]
            zone_y = model.zones_y[fixture.zone]

            clauses = [
                x_dist >= zone_x - fixture_x - M*(1-p),
                x_dist >= fixture_x - zone_x - M*(1-p),
                x_dist <= zone_x - fixture_x + M*x_further,
                x_dist <= fixture_x - zone_x + M*(1-x_further),
                x_dist <= M*p,

                y_dist >= zone_y - fixture_y - M*(1-p),
                y_dist >= fixture_y - zone_y - M*(1-p),
                y_dist <= zone_y - fixture_y + M*y_further,
                y_dist <= fixture_y - zone_y + M*(1-y_further),
                y_dist <= M*p,
            ]
            return get_clause(clauses, current_clause)
        elif current_clause == 1:
            return x_dist <= 0
        elif current_clause == 2:
            return y_dist <= 0
        else:
            return pyo.Constraint.Skip

    model.get_fixture_zone_distance = pyo.Constraint(
        model.fixtures, pyo.RangeSet(clause_count := 10), rule=get_fixture_zone_distance)

    def get_zone_center_distance(model: KitchenModel, zone: str, current_clause: int) -> Any:
        """how far is the zone center from the optimum"""
        zone_obj = next(z for z in kitchen.zones if z.name == zone)
        M = max_canvas_size

        x_dist = model.zones_x_dist[zone]
        x_further = model.zones_x_further[zone]
        y_dist = model.zones_y_dist[zone]
        y_further = model.zones_y_further[zone]

        if zone_obj.optimal_center is not None:
            zone_x = model.zones_x[zone]
            optimal_x = zone_obj.optimal_center[0]
            zone_y = model.zones_y[zone]
            optimal_y = zone_obj.optimal_center[1]

            clauses = [
                x_dist >= optimal_x - zone_x,
                x_dist >= zone_x - optimal_x,
                x_dist <= optimal_x - zone_x + M*x_further,
                x_dist <= zone_x - optimal_x + M*(1-x_further),

                y_dist >= optimal_y - zone_y,
                y_dist >= zone_y - optimal_y,
                y_dist <= optimal_y - zone_y + M*y_further,
                y_dist <= zone_y - optimal_y + M*(1-y_further),
            ]
            return get_clause(clauses, current_clause)
        elif current_clause == 1:
            return x_dist <= 0
        elif current_clause == 2:
            return y_dist <= 0
        else:
            return pyo.Constraint.Skip

    model.get_zone_center_distance = pyo.Constraint(
        model.zones, pyo.RangeSet(clause_count := 8), rule=get_zone_center_distance)

    # TARGET RULES

    def get_fixture_target_distance(model: KitchenModel, fixture: Fixture, current_clause: int) -> Any:
        """calculates the distance each fixture has from the target (plumbing etc.)"""
        p = model.present[fixture]
        M = max_canvas_size

        x_dist = model.fixtures_target_x_dist[fixture]
        x_further = model.fixtures_target_x_further[fixture]
        y_dist = model.fixtures_target_y_dist[fixture]
        y_further = model.fixtures_target_y_further[fixture]

        if fixture.type in kitchen.targets:
            fixture_x = model.fixtures_x[fixture]
            target_x = kitchen.targets[fixture.type].x
            fixture_y = model.fixtures_y[fixture]
            target_y = kitchen.targets[fixture.type].y

            clauses = [
                x_dist >= target_x - fixture_x - M*(1-p),
                x_dist >= fixture_x - target_x - M*(1-p),
                x_dist <= target_x - fixture_x + M*x_further,
                x_dist <= fixture_x - target_x + M*(1-x_further),
                x_dist <= M*p,

                y_dist >= target_y - fixture_y - M*(1-p),
                y_dist >= fixture_y - target_y - M*(1-p),
                y_dist <= target_y - fixture_y + M*y_further,
                y_dist <= fixture_y - target_y + M*(1-y_further),
                y_dist <= M*p,
            ]
            return get_clause(clauses, current_clause)
        elif current_clause == 1:
            return x_dist <= 0
        elif current_clause == 2:
            return y_dist <= 0
        else:
            return pyo.Constraint.Skip

    model.get_fixture_target_distance = pyo.Constraint(
        model.fixtures, pyo.RangeSet(clause_count := 10), rule=get_fixture_target_distance)

    # VERTICAL CONTINUITY RULES
    # for some reason, these constraints perform poorly on glpk

    enable_continuity_constraints = True

    def vertical_continuity_segments_beginning(model: KitchenModel, segment1: Segment, segment2: Segment, current_clause: int) -> Any:
        """keeps a record of segments (segment1) which begin *in the middle* of the segment (segment2) above/below them \n
        vertical continuity is broken <=> segment1.used & segment1.offset > segment2.offset & segment1.offset < segment2.offst + segment2.width"""
        begins = model.segment_begins_before[segment1, segment2]
        ends = model.segment_ends_after[segment1, segment2]
        intersects = model.segment_intersects[segment1, segment2]
        # the approach below seems to be more effective (in CBC) than using model.segments_offset[segmentX] directly
        offset1 = segment1.part.position.group_offset + model.parts_padding[segment1.part] + \
            sum(model.widths[s] for s in segment1.part.segments if s.number < segment1.number)
        offset2 = segment2.part.position.group_offset + model.parts_padding[segment2.part] + \
            sum(model.widths[s] for s in segment2.part.segments if s.number < segment2.number)
        width2 = model.widths[segment2]
        M = max_canvas_size

        if segment1 is not segment2 and segment1.part is not segment2.part and segment1.part.position.group_number == segment2.part.position.group_number:
            return get_clause([
                (0, - offset1 + (offset2 + vertical_continuity_tolerance) + M*begins, M),
                (0, offset1 - (offset2 + width2 - vertical_continuity_tolerance) + M*ends, M),
                (0, begins + ends + model.used[segment1] - 3*intersects, 2),
                # in CBC, the clauses below make it faster (but when all four are active, it becomes slower)
                # model.segment_begins_before[segment1, segment2.previous] >= model.segment_begins_before[segment1, segment2] if not segment2.is_first else pyo.Constraint.Skip,
                model.segment_begins_before[segment1.previous, segment2]
                <= model.segment_begins_before[segment1, segment2] if not segment1.is_first else pyo.Constraint.Skip,
                model.segment_ends_after[segment1, segment2.previous]
                <= model.segment_ends_after[segment1, segment2] if not segment2.is_first else pyo.Constraint.Skip,
                model.segment_ends_after[segment1.previous, segment2]
                >= model.segment_ends_after[segment1, segment2] if not segment1.is_first else pyo.Constraint.Skip,
            ], current_clause)
        else:
            return pyo.Constraint.Skip

    if enable_continuity_constraints:
        model.vertical_continuity_segments_beginning = pyo.Constraint(
            model.segments, model.segments, pyo.RangeSet(clause_count := 6), rule=vertical_continuity_segments_beginning)

    def vertical_continuity_part_ending(model: KitchenModel, part: KitchenPart, segment: Segment, current_clause: int) -> Any:
        """notes that the part ending is situated in the middle of the segment above/below"""
        begins = model.part_segment_begins_before[part, segment]
        ends = model.part_segment_ends_after[part, segment]
        intersects = model.part_segment_intersects[part, segment]
        offset1 = part.position.group_offset + model.parts_padding[part] + sum(model.widths[s] for s in part.segments)
        offset2 = segment.part.position.group_offset + model.parts_padding[segment.part] + \
            sum(model.widths[s] for s in segment.part.segments if s.number < segment.number)
        width2 = model.widths[segment]
        M = max_canvas_size

        if part is not segment.part and part.position.group_number == segment.part.position.group_number:
            return get_clause([
                (0, - offset1 + (offset2 + vertical_continuity_tolerance) + M*begins, M),
                (0, offset1 - (offset2 + width2 - vertical_continuity_tolerance) + M*ends, M),
                (0, begins + ends - 2*intersects, 1),
                model.part_segment_begins_before[part, segment.previous]
                >= model.part_segment_begins_before[part, segment] if not segment.is_first else pyo.Constraint.Skip,
                model.part_segment_ends_after[part, segment.previous]
                <= model.part_segment_ends_after[part, segment] if not segment.is_first else pyo.Constraint.Skip
            ], current_clause)
        else:
            return pyo.Constraint.Skip

    if enable_continuity_constraints:
        model.vertical_continuity_part_ending = pyo.Constraint(
            model.parts, model.segments, pyo.RangeSet(clause_count := 5), rule=vertical_continuity_part_ending)

    # WIDTH PATTERN RULES

    def is_previous_width_not_same(model: KitchenModel, segment: Segment) -> Any:
        """does the previous segment have almost the same width as the current segment? (we use negation here) \n
        segments_width_not_same <=> (segments_width_difference >= width_same_tolerance)"""
        M = max_fixture_width
        return (0, width_same_tolerance - model.segments_width_difference[segment] + M * model.segments_width_not_same[segment], M)

    model.is_previous_width_not_same = pyo.Constraint(model.segments, rule=is_previous_width_not_same)

    def is_previous_width_different(model: KitchenModel, segment: Segment) -> Any:
        """does the previous segment have different width than the current segment? \n
        segments_width_really_different <=> (segments_width_difference >= width_different_tolerance)"""
        M = max_fixture_width
        return (0, width_different_tolerance - model.segments_width_difference[segment] + M * model.segments_width_really_different[segment], M)

    model.is_previous_width_different = pyo.Constraint(model.segments, rule=is_previous_width_different)

    def different_implies_not_same(model: KitchenModel, segment: Segment) -> Any:
        return model.segments_width_really_different[segment] <= model.segments_width_not_same[segment]

    model.different_implies_not_same = pyo.Constraint(model.segments, rule=different_implies_not_same)

    def is_penultimate_width_similar(model: KitchenModel, segment: Segment) -> Any:
        """segments_penult_similar <=> (segments_penult_width_difference <= width_penult_similar_tolerance)"""
        M = max_fixture_width
        return (0, model.segments_penult_width_difference[segment] - width_penult_similar_tolerance + M * model.segments_penult_similar[segment], M)

    model.is_penultimate_width_similar = pyo.Constraint(model.segments, rule=is_penultimate_width_similar)

    def is_aba_pattern(model: KitchenModel, segment: Segment) -> Any:
        """segments form ABA pattern <=> the A segments have similar width & the B segment has distinct width"""
        if segment.is_first or segment.previous is None or segment.previous.is_first:
            return model.segments_pattern_aba[segment] <= 0
        else:
            return (0, model.segments_penult_similar[segment] + model.segments_width_really_different[segment] - 2*model.segments_pattern_aba[segment], 1)

    model.is_aba_pattern = pyo.Constraint(model.segments, rule=is_aba_pattern)

    # TODO: piping/plumbing rule, storage & worktop space, rational use of fixtures (one sink is enough)


def set_objective(model: KitchenModel) -> None:
    def fitness(model: KitchenModel) -> Any:
        # prefer more present fixtures
        present_count = sum(model.present[fixture] for fixture in model.fixtures)

        # prefer larger total width
        width_coeff = (sum(model.widths[segment] for segment in model.segments) -
                       sum(part.width for part in model.parts)) / 2

        # penalize width differences
        width_patterns = sum(model.segments_width_not_same[segment] for segment in model.segments) * -1
        width_patterns += sum(model.segments_pattern_aba[segment] for segment in model.segments)

        # minimize zone distances
        zone_dist = sum(model.fixtures_zone_x_dist[fixture] +
                        model.fixtures_zone_y_dist[fixture] for fixture in model.fixtures) / -10

        # minimize target distances
        target_dist = sum(model.fixtures_target_x_dist[fixture] +
                          model.fixtures_target_y_dist[fixture] for fixture in model.fixtures) / -10

        # minimize distance from optimal centers
        center_dist = sum(model.zones_x_dist[zone] + model.zones_y_dist[zone] for zone in model.zones) / -10

        # minimize vertical non-continuities
        intersections = sum(model.segment_intersects[s, t] for s in model.segments for t in model.segments) / -5
        intersections += sum(model.part_segment_intersects[p, s] for s in model.segments for p in model.parts) / -5

        return present_count + width_coeff + width_patterns + target_dist + zone_dist + center_dist + intersections

    model.fitness = pyo.Objective(rule=fitness, sense=pyo.maximize)


def find_model(model: KitchenModel) -> None:
    # opt = pyo.SolverFactory('glpk')
    # opt = pyo.SolverFactory('cbc')
    opt = pyo.SolverFactory('gurobi_direct')
    result_obj = opt.solve(model, tee=True)
    model.pprint()


def save_result(kitchen: Kitchen, model: KitchenModel) -> None:
    for part in kitchen.parts:
        part.position.padding = pyo.value(model.parts_padding[part])

    for segment in kitchen.segments:
        segment.width = pyo.value(model.widths[segment], exception=False)

        if segment.width is None:
            segment.width = 0

        for fixture in kitchen.fixtures:
            if pyo.value(model.pairs[segment, fixture], exception=False):
                segment.fixture = fixture
