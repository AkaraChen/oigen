#!/usr/bin/env python3
"""Example: Generate graph data."""

from oigen import workflow, Graph, Int


@workflow()
def graph_data():
    """Generate a random undirected graph."""
    return Graph(n=Int(5, 10), m=Int(5, 15))


@workflow()
def directed_graph_data():
    """Generate a random directed graph."""
    return Graph(n=Int(5, 10), m=Int(10, 20), directed=True)


if __name__ == "__main__":
    # Generate undirected graph files
    graph_data.run(output="./output/graph", count=5)

    # Generate directed graph files
    directed_graph_data.run(output="./output/directed_graph", count=5)
