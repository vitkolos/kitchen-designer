from kitchen import Kitchen, KitchenItem
import random
import matplotlib.pyplot as plt


def draw(data: Kitchen):
    line_height = 5
    line_distance = 10
    font_size = 10

    print(f"WIDTH {data.width}")

    x = 0
    y = 0
    fig, ax = plt.subplots()
    eps = 0.2
    line = plt.Rectangle((x-eps, y-eps), data.width+2*eps,
                         line_height+2*eps, fill=False, ec='red')
    ax.add_patch(line)
    # y += line_distance + line_height

    for item in data.items:
        w = random.randint(item.width_min, item.width_max)
        print(f"{item.name} {w}")
        color = '#555555'

        match item.zone:
            case 'cleaning': color = '#0077ff'
            case 'storage': color = '#914400'
            case 'cooking': color = '#cc0000'

        line = plt.Rectangle((x, y), w, line_height, fc=color+'33', ec=color+'77')
        ax.add_patch(line)
        ax.annotate(item.name, (x+1, y+line_height-1), color=color,
                    fontsize=font_size)
        x += w

    ax.invert_yaxis()
    ax.set_axis_off()
    plt.axis('equal')

    plt.show()
