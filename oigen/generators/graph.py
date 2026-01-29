"""
Graph generator for random graph structures.
"""

from dataclasses import dataclass
from random import Random
from typing import Any

from oigen.errors import ConstraintError
from oigen.generators import BaseGenerator


@dataclass
class GraphData:
    """Generated graph data structure.

    Attributes:
        n: Number of nodes.
        m: Number of edges.
        edges: List of (u, v) tuples representing edges (1-indexed).
        directed: Whether the graph is directed.
        node_values: Optional list of node values (1-indexed, index 0 is unused).
    """
    n: int
    m: int
    edges: list[tuple[int, int]]
    directed: bool = False
    node_values: list[Any] | None = None

    def __str__(self) -> str:
        """Format graph for output (OI-style)."""
        lines = [f"{self.n} {self.m}"]
        if self.node_values is not None:
            lines.append(" ".join(str(v) for v in self.node_values[1:]))
        for u, v in self.edges:
            lines.append(f"{u} {v}")
        return "\n".join(lines)


class Graph(BaseGenerator):
    """Generator for random graph structures.

    Args:
        n: Number of nodes (or generator for n).
        m: Number of edges (or generator for m).
        node_value: Optional generator for node values.
        directed: If True, generate directed graph (default False).
        allow_self_loops: If True, allow edges from a node to itself (default False).
        allow_multi_edges: If True, allow multiple edges between same nodes (default False).

    Raises:
        ConstraintError: If constraints are invalid or edge count exceeds maximum.

    Example:
        >>> gen = Graph(n=5, m=7)  # Undirected simple graph
        >>> gen = Graph(n=5, m=7, directed=True)  # Directed graph
        >>> gen = Graph(n=5, m=20, allow_multi_edges=True)  # Multi-graph
    """

    def __init__(
        self,
        n: int | BaseGenerator,
        m: int | BaseGenerator,
        node_value: BaseGenerator | None = None,
        directed: bool = False,
        allow_self_loops: bool = False,
        allow_multi_edges: bool = False,
    ):
        self.n = n
        self.m = m
        self.node_value = node_value
        self.directed = directed
        self.allow_self_loops = allow_self_loops
        self.allow_multi_edges = allow_multi_edges
        self.validate()

    def validate(self) -> None:
        if isinstance(self.n, int) and self.n < 1:
            raise ConstraintError(
                f"Graph: n ({self.n}) must be >= 1",
                suggestion="Use at least 1 node for the graph",
            )
        if isinstance(self.m, int) and self.m < 0:
            raise ConstraintError(
                f"Graph: m ({self.m}) cannot be negative",
                suggestion="Use a non-negative edge count",
            )
        if self.node_value is not None and not isinstance(self.node_value, BaseGenerator):
            raise ConstraintError(
                f"Graph: node_value must be a generator, got {type(self.node_value).__name__}",
                suggestion="Use a generator like Int() or Dict() for node values",
            )

    def _max_edges(self, n: int) -> int:
        """Calculate maximum possible edges for given constraints."""
        if self.allow_multi_edges:
            return float("inf")  # Unlimited with multi-edges

        if self.directed:
            # n * (n-1) for directed, + n if self-loops allowed
            max_e = n * (n - 1)
            if self.allow_self_loops:
                max_e += n
        else:
            # n * (n-1) / 2 for undirected, + n if self-loops allowed
            max_e = n * (n - 1) // 2
            if self.allow_self_loops:
                max_e += n

        return max_e

    def _generate_edges(
        self,
        n: int,
        m: int,
        rng: Random,
    ) -> list[tuple[int, int]]:
        """Generate random edges for the graph."""
        if self.allow_multi_edges:
            # With multi-edges, just generate random edges
            edges = []
            for _ in range(m):
                if self.allow_self_loops:
                    u = rng.randint(1, n)
                    v = rng.randint(1, n)
                else:
                    u = rng.randint(1, n)
                    v = rng.randint(1, n)
                    while v == u:
                        v = rng.randint(1, n)
                edges.append((u, v))
            return edges

        # Without multi-edges, use a set to track existing edges
        edge_set: set[tuple[int, int]] = set()
        edges: list[tuple[int, int]] = []

        attempts = 0
        max_attempts = m * 10 + 1000  # Prevent infinite loop

        while len(edges) < m and attempts < max_attempts:
            attempts += 1

            if self.allow_self_loops:
                u = rng.randint(1, n)
                v = rng.randint(1, n)
            else:
                u = rng.randint(1, n)
                v = rng.randint(1, n)
                while v == u:
                    v = rng.randint(1, n)

            # Normalize edge for undirected graphs
            if not self.directed and u > v:
                u, v = v, u

            if (u, v) not in edge_set:
                edge_set.add((u, v))
                # Store original order for directed, normalized for undirected
                if self.directed:
                    edges.append((rng.choice([u, v]) if u == v else (u, v) if rng.random() < 0.5 else (v, u)))
                    # Actually we already have u, v in correct order, just append
                    edges[-1] = (u, v)  # Fix: just use what we generated
                else:
                    edges.append((u, v))

        # Shuffle to randomize order
        rng.shuffle(edges)
        return edges

    def generate(self, rng: Random) -> GraphData:
        # Resolve n and m if they're generators
        if isinstance(self.n, BaseGenerator):
            n = self.n.generate(rng)
        else:
            n = self.n

        if isinstance(self.m, BaseGenerator):
            m = self.m.generate(rng)
        else:
            m = self.m

        if n < 1:
            raise ConstraintError(
                f"Graph: generated n ({n}) must be >= 1",
                suggestion="Ensure your n generator produces values >= 1",
            )

        if m < 0:
            raise ConstraintError(
                f"Graph: generated m ({m}) cannot be negative",
                suggestion="Ensure your m generator produces non-negative values",
            )

        # Check edge count against maximum
        max_e = self._max_edges(n)
        if m > max_e:
            graph_type = "directed" if self.directed else "undirected"
            loops_str = "with" if self.allow_self_loops else "without"
            raise ConstraintError(
                f"Graph: requested {m} edges, but maximum for {graph_type} simple graph "
                f"with {n} nodes ({loops_str} self-loops) is {max_e}",
                suggestion="Use allow_multi_edges=True to allow multiple edges between nodes, "
                           "or reduce the edge count",
            )

        edges = self._generate_edges(n, m, rng)

        # Generate node values if specified
        node_values = None
        if self.node_value is not None:
            node_values = [None] + [self.node_value.generate(rng) for _ in range(n)]

        return GraphData(
            n=n,
            m=m,
            edges=edges,
            directed=self.directed,
            node_values=node_values,
        )

    def __repr__(self) -> str:
        parts = [f"n={self.n!r}", f"m={self.m!r}"]
        if self.node_value is not None:
            parts.append(f"node_value={self.node_value!r}")
        if self.directed:
            parts.append("directed=True")
        if self.allow_self_loops:
            parts.append("allow_self_loops=True")
        if self.allow_multi_edges:
            parts.append("allow_multi_edges=True")
        return f"Graph({', '.join(parts)})"
