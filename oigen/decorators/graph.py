"""
Graph constraint decorators.
"""

from dataclasses import dataclass
from typing import Any, Callable, TypeVar

from oigen.decorators.base import Constraint, ConstraintRegistry, add_constraint
from oigen.errors import ConstraintError
from oigen.generators import BaseGenerator

F = TypeVar("F", bound=Callable[..., BaseGenerator])


# ============================================================================
# Graph Constraints
# ============================================================================


@dataclass
class DirectedConstraint(Constraint):
    """Constraint to make graph directed."""

    def validate(self, generator: BaseGenerator, registry: ConstraintRegistry) -> None:
        pass  # Always valid

    def apply(self, generator: BaseGenerator, context: dict[str, Any]) -> None:
        context["directed"] = True

    @property
    def priority(self) -> int:
        return 5  # Apply very early


@dataclass
class GraphNodeWeightConstraint(Constraint):
    """Constraint for graph node weights."""

    generator: BaseGenerator

    def validate(self, generator: BaseGenerator, registry: ConstraintRegistry) -> None:
        if not isinstance(self.generator, BaseGenerator):
            raise ConstraintError(
                f"with_node_weight: generator must be a BaseGenerator, "
                f"got {type(self.generator).__name__}",
                suggestion="Use a generator like Int(1, 100)",
            )

    def apply(self, generator: BaseGenerator, context: dict[str, Any]) -> None:
        context["node_weight"] = self.generator

    @property
    def priority(self) -> int:
        return 50


@dataclass
class GraphEdgeWeightConstraint(Constraint):
    """Constraint for graph edge weights."""

    generator: BaseGenerator

    def validate(self, generator: BaseGenerator, registry: ConstraintRegistry) -> None:
        if not isinstance(self.generator, BaseGenerator):
            raise ConstraintError(
                f"with_edge_weight: generator must be a BaseGenerator, "
                f"got {type(self.generator).__name__}",
                suggestion="Use a generator like Int(1, 100)",
            )

    def apply(self, generator: BaseGenerator, context: dict[str, Any]) -> None:
        context["edge_weight"] = self.generator

    @property
    def priority(self) -> int:
        return 50


@dataclass
class CycleConstraint(Constraint):
    """Constraint to require cycles in the graph."""

    negative: bool = False  # If True, requires negative cycle

    def validate(self, generator: BaseGenerator, registry: ConstraintRegistry) -> None:
        # Check that graph has enough edges for a cycle
        m = getattr(generator, "m", None)
        n = getattr(generator, "n", None)
        if isinstance(m, int) and isinstance(n, int):
            if m < n:
                raise ConstraintError(
                    f"with_cycle: need at least {n} edges to guarantee a cycle (n={n}), "
                    f"but m={m}",
                    suggestion="Increase edge count to at least n",
                )

        # Negative cycle requires edge weights
        if self.negative and not registry.has(GraphEdgeWeightConstraint):
            raise ConstraintError(
                "with_cycle(negative=True): requires edge weights",
                suggestion="Add @with_edge_weight(Int(-10, 10)) decorator",
            )

    def apply(self, generator: BaseGenerator, context: dict[str, Any]) -> None:
        context["has_cycle"] = True
        context["negative_cycle"] = self.negative

    @property
    def priority(self) -> int:
        return 10


@dataclass
class PathConstraint(Constraint):
    """Constraint to guarantee a path between two nodes."""

    start: int
    end: int

    def validate(self, generator: BaseGenerator, registry: ConstraintRegistry) -> None:
        n = getattr(generator, "n", None)
        if isinstance(n, int):
            if self.start < 1 or self.start > n:
                raise ConstraintError(
                    f"with_path: start ({self.start}) must be between 1 and n ({n})",
                    suggestion="Use a valid node number",
                )
            if self.end < 1 or self.end > n:
                raise ConstraintError(
                    f"with_path: end ({self.end}) must be between 1 and n ({n})",
                    suggestion="Use a valid node number",
                )

    def apply(self, generator: BaseGenerator, context: dict[str, Any]) -> None:
        context["guaranteed_path"] = (self.start, self.end)

    @property
    def priority(self) -> int:
        return 10


@dataclass
class CutVertexConstraint(Constraint):
    """Constraint for number of cut vertices (articulation points)."""

    count: int

    def validate(self, generator: BaseGenerator, registry: ConstraintRegistry) -> None:
        if self.count < 0:
            raise ConstraintError(
                f"with_cut_vertex: count ({self.count}) cannot be negative",
                suggestion="Use a non-negative count",
            )

        n = getattr(generator, "n", None)
        if isinstance(n, int) and self.count > n - 2:
            raise ConstraintError(
                f"with_cut_vertex: count ({self.count}) cannot exceed n-2 ({n-2})",
                suggestion="Reduce the cut vertex count",
            )

    def apply(self, generator: BaseGenerator, context: dict[str, Any]) -> None:
        context["cut_vertex_count"] = self.count

    @property
    def priority(self) -> int:
        return 10


@dataclass
class LongestPathConstraint(Constraint):
    """Constraint for longest path length in the graph."""

    min_val: int
    max_val: int

    def validate(self, generator: BaseGenerator, registry: ConstraintRegistry) -> None:
        if self.min_val < 1:
            raise ConstraintError(
                f"with_longest_path: min ({self.min_val}) must be >= 1",
                suggestion="Path length is measured in edges, minimum is 1",
            )
        if self.min_val > self.max_val:
            raise ConstraintError(
                f"with_longest_path: min ({self.min_val}) must be <= max ({self.max_val})",
                suggestion="Swap the min and max values",
            )

        n = getattr(generator, "n", None)
        if isinstance(n, int) and self.min_val > n - 1:
            raise ConstraintError(
                f"with_longest_path: min ({self.min_val}) cannot exceed n-1 ({n-1})",
                suggestion="Reduce the path length or increase the number of nodes",
            )

    def apply(self, generator: BaseGenerator, context: dict[str, Any]) -> None:
        context["longest_path"] = (self.min_val, self.max_val)

    @property
    def priority(self) -> int:
        return 10


@dataclass
class SelfLoopsConstraint(Constraint):
    """Constraint to allow self-loops."""

    def validate(self, generator: BaseGenerator, registry: ConstraintRegistry) -> None:
        pass

    def apply(self, generator: BaseGenerator, context: dict[str, Any]) -> None:
        context["allow_self_loops"] = True

    @property
    def priority(self) -> int:
        return 5


@dataclass
class MultiEdgesConstraint(Constraint):
    """Constraint to allow multiple edges between same nodes."""

    def validate(self, generator: BaseGenerator, registry: ConstraintRegistry) -> None:
        pass

    def apply(self, generator: BaseGenerator, context: dict[str, Any]) -> None:
        context["allow_multi_edges"] = True

    @property
    def priority(self) -> int:
        return 5


# ============================================================================
# Decorator Functions
# ============================================================================


def directed(func: F) -> F:
    """Make the graph directed.

    Example:
        @directed
        def dag():
            return Graph(n=10, m=15)
    """
    return add_constraint(DirectedConstraint())(func)


def with_node_weight(generator: BaseGenerator) -> Callable[[F], F]:
    """Add node weights to the graph using the given generator.

    Example:
        @with_node_weight(Int(1, 100))
        def weighted_graph():
            return Graph(n=10, m=15)
    """
    return add_constraint(GraphNodeWeightConstraint(generator))


def with_edge_weight(generator: BaseGenerator) -> Callable[[F], F]:
    """Add edge weights to the graph using the given generator.

    Example:
        @with_edge_weight(Int(1, 100))
        def weighted_graph():
            return Graph(n=10, m=15)
    """
    return add_constraint(GraphEdgeWeightConstraint(generator))


def with_cycle(negative: bool = False) -> Callable[[F], F]:
    """Ensure the graph contains a cycle.

    Args:
        negative: If True, ensure there's a negative cycle (requires edge weights).

    Example:
        @with_cycle()
        def cyclic_graph():
            return Graph(n=10, m=15)

        @with_cycle(negative=True)
        @with_edge_weight(Int(-10, 10))
        def negative_cycle_graph():
            return Graph(n=10, m=15)
    """
    return add_constraint(CycleConstraint(negative=negative))


def with_path(start: int, end: int) -> Callable[[F], F]:
    """Guarantee a path exists between two nodes.

    Args:
        start: Starting node (1-indexed).
        end: Ending node (1-indexed).

    Example:
        @with_path(1, 10)
        def connected_graph():
            return Graph(n=10, m=15)
    """
    return add_constraint(PathConstraint(start, end))


def with_cut_vertex(count: int) -> Callable[[F], F]:
    """Constrain the number of cut vertices (articulation points).

    Args:
        count: Required number of cut vertices.

    Example:
        @with_cut_vertex(2)
        def graph_with_cuts():
            return Graph(n=10, m=15)
    """
    return add_constraint(CutVertexConstraint(count))


def with_longest_path(min_val: int, max_val: int | None = None) -> Callable[[F], F]:
    """Constrain the longest path length in the graph.

    Args:
        min_val: Minimum longest path (or exact if max_val is None).
        max_val: Maximum longest path.

    Example:
        @with_longest_path(5, 8)
        def bounded_path_graph():
            return Graph(n=10, m=15)
    """
    if max_val is None:
        max_val = min_val
    return add_constraint(LongestPathConstraint(min_val, max_val))


def allow_self_loops(func: F) -> F:
    """Allow self-loops in the graph (edges from a node to itself).

    Example:
        @allow_self_loops
        def graph_with_loops():
            return Graph(n=10, m=15)
    """
    return add_constraint(SelfLoopsConstraint())(func)


def allow_multi_edges(func: F) -> F:
    """Allow multiple edges between the same pair of nodes.

    Example:
        @allow_multi_edges
        def multigraph():
            return Graph(n=10, m=30)
    """
    return add_constraint(MultiEdgesConstraint())(func)
