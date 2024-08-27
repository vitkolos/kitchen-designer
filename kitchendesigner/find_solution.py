from kitchen import Kitchen, KitchenSegment
import random
import pyomo.environ as pyo


def solve(kitchen: Kitchen) -> None:
    # dummy data
    for part in kitchen.parts:
        part.segments = []

        for item in kitchen.items:
            w = random.randint(item.width_min, item.width_max)
            part.segments.append(KitchenSegment(0, w, item))

        part.segments.append(KitchenSegment(0, 0, None))
