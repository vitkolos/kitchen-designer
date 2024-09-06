import process_args
import load_input
import find_solution
import produce_output

def main() -> None:
    args = process_args.process()
    kitchen = load_input.load(args.input)
    find_solution.solve(kitchen, args)
    produce_output.write(kitchen, args.output)
    produce_output.draw(kitchen)


if __name__ == '__main__':
    main()
