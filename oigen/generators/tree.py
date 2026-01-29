"""
Tree generator for random tree structures.
"""

from dataclasses import dataclass
from random import Random
from typing import Any

from oigen.errors import ConstraintError
from oigen.generators import BaseGenerator


@dataclass
class TreeData:
    """Generated tree data structure.

    Attributes:
        n: Number of nodes.
        edges: List of (u, v) tuples representing edges (1-indexed).
        node_values: Optional list of node values (1-indexed, index 0 is unused).
    """
    n: int
    edges: list[tuple[int, int]]
    node_values: list[Any] | None = None

    def __str__(self) -> str:
        """Format tree for output (OI-style)."""
        lines = [str(self.n)]
        if self.node_values is not None:
            # Node values on second line (space-separated, nodes 1 to n)
            lines.append(" ".join(str(v) for v in self.node_values[1:]))
        for u, v in self.edges:
            lines.append(f"{u} {v}")
        return "\n".join(lines)


class Tree(BaseGenerator):
    """Generator for random tree structures.

    Generates a random tree with n nodes using Prüfer sequence method,
    ensuring the tree is connected and acyclic.

    Args:
        n: Number of nodes (or generator for n).
        node_value: Optional generator for node values.

    Raises:
        ConstraintError: If n < 1.

    Example:
        >>> gen = Tree(n=10)  # Tree with 10 nodes
        >>> gen = Tree(n=10, node_value=Int(1, 100))  # With node values
    """

    def __init__(
        self,
        n: int | BaseGenerator,
        node_value: BaseGenerator | None = None,
    ):
        self.n = n
        self.node_value = node_value
        self.validate()

    def validate(self) -> None:
        if isinstance(self.n, int) and self.n < 1:
            raise ConstraintError(
                f"Tree: n ({self.n}) must be >= 1",
                suggestion="Use at least 1 node for the tree",
            )
        if self.node_value is not None and not isinstance(self.node_value, BaseGenerator):
            raise ConstraintError(
                f"Tree: node_value must be a generator, got {type(self.node_value).__name__}",
                suggestion="Use a generator like Int() or Dict() for node values",
            )

    def _generate_tree_edges(self, n: int, rng: Random) -> list[tuple[int, int]]:
        """Generate random tree edges using random parent assignment.

        For each node i from 2 to n, randomly select a parent from nodes 1 to i-1.
        This guarantees a connected, acyclic tree.
        """
        if n == 1:
            return []

        edges: list[tuple[int, int]] = []
        for i in range(2, n + 1):
            parent = rng.randint(1, i - 1)
            edges.append((parent, i))

        # Shuffle edges for variety
        rng.shuffle(edges)
        return edges

    def generate(self, rng: Random) -> TreeData:
        # Resolve n if it's a generator
        if isinstance(self.n, BaseGenerator):
            n = self.n.generate(rng)
        else:
            n = self.n

        if n < 1:
            raise ConstraintError(
                f"Tree: generated n ({n}) must be >= 1",
                suggestion="Ensure your n generator produces values >= 1",
            )

        edges = self._generate_tree_edges(n, rng)

        # Generate node values if specified
        node_values = None
        if self.node_value is not None:
            # Index 0 is unused, nodes are 1-indexed
            node_values = [None] + [self.node_value.generate(rng) for _ in range(n)]

        return TreeData(n=n, edges=edges, node_values=node_values)

    def __repr__(self) -> str:
        if self.node_value is None:
            return f"Tree(n={self.n!r})"
        return f"Tree(n={self.n!r}, node_value={self.node_value!r})"
