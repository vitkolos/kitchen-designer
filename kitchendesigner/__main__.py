import load_input
import find_solution
import draw_output

def main() -> None:
    kitchen = load_input.load()
    find_solution.solve(kitchen)
    draw_output.draw(kitchen)


if __name__ == '__main__':
    main()
