import argparse
from dataclasses import dataclass


@dataclass
class Args:
    input: str
    output: str
    solver: str | None
    model: str | None
    structure: bool


def process() -> Args:
    parser = argparse.ArgumentParser()
    parser.add_argument('input')
    parser.add_argument('output')
    parser.add_argument("-s", "--solver")
    parser.add_argument("-m", "--model")
    parser.add_argument("--structure", action='store_true')
    args = parser.parse_args()
    return Args(args.input, args.output, args.solver, args.model, args.structure)
