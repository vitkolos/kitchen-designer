import argparse
from typing import Any
from dataclasses import dataclass


@dataclass
class Args:
    input: str
    output: str
    solver: str | None
    model: str | None


def process() -> Args:
    parser = argparse.ArgumentParser()
    parser.add_argument('input')
    parser.add_argument('output')
    parser.add_argument("-s", "--solver")
    parser.add_argument("-m", "--model")
    args = parser.parse_args()
    return Args(args.input, args.output, args.solver, args.model)
