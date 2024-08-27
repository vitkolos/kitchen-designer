from kitchen import Kitchen
import matplotlib.pyplot as plt
import matplotlib.patches as patches


def draw(kitchen: Kitchen) -> None:
    part_distance = 10
    font_size = 10
    fig, ax = plt.subplots()
    y = 0.0
    eps = 0.2

    for part in kitchen.parts:
        y -= part.depth
        x = 0.0

        print(f"PART width {part.width}")
        rectangle = patches.Rectangle(
            (x-eps, y-eps), part.width+2*eps, part.depth+2*eps, fill=False, ec='red')
        ax.add_patch(rectangle)

        for segment in part.segments:
            print(f"segment {segment.number}, fixture {segment.fixture}, width {segment.width}")
            color = '#555555'

            if segment.fixture is not None:
                match segment.fixture.zone:
                    case 'cleaning': color = '#0077ff'
                    case 'storage': color = '#914400'
                    case 'cooking': color = '#cc0000'

            rectangle = patches.Rectangle(
                (x, y), segment.width, part.depth, fc=color+'33', ec=color+'77')
            ax.add_patch(rectangle)
            ax.annotate(str(segment.fixture), (x+1, y+1), color=color,
                        fontsize=font_size)
            x += segment.width

        print()
        y -= part_distance

    # ax.invert_yaxis()
    # ax.set_axis_off()
    plt.axis('equal')
    plt.show()
