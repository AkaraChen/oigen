#!/usr/bin/env python3
"""Example: Generate tree data."""

from oigen import workflow, Tree, Int


@workflow()
def tree_data():
    """Generate a random tree with node values."""
    return Tree(n=Int(5, 15), node_value=Int(1, 100))


if __name__ == "__main__":
    # Generate 5 test files
    tree_data.run(output="./output/tree", count=5)
