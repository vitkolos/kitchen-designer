from kitchen import Kitchen
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import math


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

        print(f"PART width {part.width}")
        rectangle = patches.Rectangle((x-eps, y-eps), part.width+2*eps, part.depth + 2*eps,
                                      angle=angle, rotation_point=(rx, ry), fill=False, ec='red')
        ax.add_patch(rectangle)

        for segment in part.segments:
            print(f"segment {segment.number}, fixture {segment.fixture}, width {segment.width}")
            # print(repr(segment))
            color = '#555555'

            if segment.fixture is not None:
                match segment.fixture.zone:
                    case 'cleaning': color = '#0077ff'
                    case 'storage': color = '#914400'
                    case 'cooking': color = '#cc0000'

            rectangle = patches.Rectangle((x, y), segment.width, part.depth, angle=angle,
                                          rotation_point=(rx, ry), fc=color+'33', ec=color+'77')
            ax.add_patch(rectangle)
            lx, ly = rotate_point_deg((x+segment.width/2, y+part.depth/2), (rx, ry), angle)
            ax.text(lx, ly, str(segment.fixture), color=color, fontsize=font_size,
                    verticalalignment='center', horizontalalignment='center')
            x += segment.width

        print()

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
