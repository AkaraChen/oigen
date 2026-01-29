#!/usr/bin/env python3
"""Example: Generate sequence data."""

from oigen import workflow, Sequence, Int


@workflow()
def sequence_data():
    """Generate a sequence of random integers."""
    return Sequence(Int(1, 1000), length=(5, 20))


if __name__ == "__main__":
    # Generate 5 test files
    sequence_data.run(output="./output/sequence", count=5)
