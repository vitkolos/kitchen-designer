from kitchen import Kitchen, KitchenItem
import random


def draw(data: Kitchen):
    print(f"WIDTH {data.width}")

    for item in data.items:
        w = random.randint(item.width_min, item.width_max)
        print(f"{item.name} {w}")
