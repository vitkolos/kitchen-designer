from kitchen import Kitchen
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import math
import json
from typing import Any


def draw(kitchen: Kitchen) -> None:
    font_size = 10
    fig, ax = plt.subplots()
    eps = 0.2

    for part in kitchen.parts:
        x = part.position.x
        y = part.position.y
        angle = part.position.angle

        if part.is_top:
            rectangle_real = patches.Rectangle((x, y), part.width, part.depth, angle=angle,
                                               rotation_point=(x, y), fill=False, ec='#00000019', hatch='//')
            ax.add_patch(rectangle_real)
            x, y = rotate_point_deg((x, y + part.depth * 1.5), (x, y), angle)

        rx = x
        ry = y

        rectangle = patches.Rectangle((x-eps, y-eps), part.width+2*eps, part.depth + 2*eps,
                                      angle=angle, rotation_point=(rx, ry), fill=False, ec='red')
        ax.add_patch(rectangle)

        x += part.position.padding

        for segment in part.segments:
            color = '#555555'

            if segment.fixture is not None:
                zone_obj = next(z for z in kitchen.zones if z.name == segment.fixture.zone)

                if zone_obj.color:
                    color = zone_obj.color

            rectangle = patches.Rectangle((x, y), segment.width, part.depth, angle=angle,
                                          rotation_point=(rx, ry), fc=color+'33', ec=color+'77')
            ax.add_patch(rectangle)
            lx, ly = rotate_point_deg((x+segment.width/2, y+part.depth/2), (rx, ry), angle)
            ax.text(lx, ly, f"{segment.number}. {segment.fixture}", color=color, fontsize=font_size,
                    verticalalignment='center', horizontalalignment='center')
            x += segment.width

    # ax.invert_yaxis()
    # ax.set_axis_off()
    plt.axis('equal')
    plt.show()


def rotate_point_deg(point: tuple[float, float], around: tuple[float, float], angle: float) -> tuple[float, float]:
    angle1 = math.radians(angle)
    px, py = point
    ax, ay = around
    qx = (px-ax)*math.cos(angle1)-(py-ay)*math.sin(angle1)+ax
    qy = (px-ax)*math.sin(angle1)+(py-ay)*math.cos(angle1)+ay
    return qx, qy


def write(kitchen: Kitchen, file_name: str) -> None:
    output: dict[str, dict[str, Any]] = {}

    for part in kitchen.parts:
        output[part.name] = {}
        output[part.name]['padding'] = part.position.padding
        output[part.name]['fixtures'] = []

        for segment in part.segments:
            if segment.fixture is not None:
                output[part.name]['fixtures'].append({'fixture': segment.fixture.name, 'width': segment.width})

    with open(file_name, 'w') as output_file:
        json.dump(output, output_file, indent=4)
