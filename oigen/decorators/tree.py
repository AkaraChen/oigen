"""
Tree constraint decorators.
"""

from dataclasses import dataclass
from typing import Any, Callable, TypeVar

from oigen.decorators.base import Constraint, ConstraintRegistry, add_constraint
from oigen.errors import ConstraintError
from oigen.generators import BaseGenerator


F = TypeVar("F", bound=Callable[..., BaseGenerator])


# ============================================================================
# Tree Constraints
# ============================================================================


@dataclass
class NodeWeightConstraint(Constraint):
    """Constraint for tree node weights."""

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
        return 50  # Apply weights early


@dataclass
class EdgeWeightConstraint(Constraint):
    """Constraint for tree edge weights."""

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
class DiameterConstraint(Constraint):
    """Constraint for tree diameter (longest path length)."""

    min_val: int
    max_val: int

    def validate(self, generator: BaseGenerator, registry: ConstraintRegistry) -> None:
        if self.min_val < 1:
            raise ConstraintError(
                f"with_diameter: min ({self.min_val}) must be >= 1",
                suggestion="Diameter is measured in edges, minimum is 1",
            )
        if self.min_val > self.max_val:
            raise ConstraintError(
                f"with_diameter: min ({self.min_val}) must be <= max ({self.max_val})",
                suggestion="Swap the min and max values",
            )

        # Check against n if available
        n = getattr(generator, "n", None)
        if isinstance(n, int) and self.min_val > n - 1:
            raise ConstraintError(
                f"with_diameter: min diameter ({self.min_val}) cannot exceed n-1 ({n-1})",
                suggestion="Reduce the diameter or increase the number of nodes",
            )

    def apply(self, generator: BaseGenerator, context: dict[str, Any]) -> None:
        context["diameter"] = (self.min_val, self.max_val)

    @property
    def priority(self) -> int:
        return 10  # Structural constraints first


@dataclass
class CentroidConstraint(Constraint):
    """Constraint for number of tree centroids."""

    count: int  # 1 or 2

    def validate(self, generator: BaseGenerator, registry: ConstraintRegistry) -> None:
        if self.count not in (1, 2):
            raise ConstraintError(
                f"with_centroid: count must be 1 or 2, got {self.count}",
                suggestion="A tree has either 1 or 2 centroids",
            )

    def apply(self, generator: BaseGenerator, context: dict[str, Any]) -> None:
        context["centroid_count"] = self.count

    @property
    def priority(self) -> int:
        return 10


@dataclass
class DepthConstraint(Constraint):
    """Constraint for tree depth (max distance from root)."""

    min_val: int
    max_val: int

    def validate(self, generator: BaseGenerator, registry: ConstraintRegistry) -> None:
        if self.min_val < 1:
            raise ConstraintError(
                f"with_depth: min ({self.min_val}) must be >= 1",
                suggestion="Depth is measured in edges from root, minimum is 1",
            )
        if self.min_val > self.max_val:
            raise ConstraintError(
                f"with_depth: min ({self.min_val}) must be <= max ({self.max_val})",
                suggestion="Swap the min and max values",
            )

        # Check against n if available
        n = getattr(generator, "n", None)
        if isinstance(n, int) and self.min_val > n - 1:
            raise ConstraintError(
                f"with_depth: min depth ({self.min_val}) cannot exceed n-1 ({n-1})",
                suggestion="Reduce the depth or increase the number of nodes",
            )

        # Check compatibility with diameter
        diameter = registry.get_one(DiameterConstraint)
        if diameter is not None:
            # Depth must be at least diameter / 2
            min_depth_from_diameter = (diameter.min_val + 1) // 2
            if self.max_val < min_depth_from_diameter:
                raise ConstraintError(
                    f"with_depth: max depth ({self.max_val}) is too small for "
                    f"diameter ({diameter.min_val}-{diameter.max_val})",
                    suggestion=f"Depth must be at least {min_depth_from_diameter} for this diameter",
                )

    def apply(self, generator: BaseGenerator, context: dict[str, Any]) -> None:
        context["depth"] = (self.min_val, self.max_val)

    @property
    def priority(self) -> int:
        return 10


# ============================================================================
# Decorator Functions
# ============================================================================


def with_node_weight(generator: BaseGenerator) -> Callable[[F], F]:
    """Add node weights to the tree using the given generator.

    Example:
        @with_node_weight(Int(1, 100))
        def weighted_tree():
            return Tree(n=10)
    """
    return add_constraint(NodeWeightConstraint(generator))


def with_edge_weight(generator: BaseGenerator) -> Callable[[F], F]:
    """Add edge weights to the tree using the given generator.

    Example:
        @with_edge_weight(Int(1, 100))
        def weighted_tree():
            return Tree(n=10)
    """
    return add_constraint(EdgeWeightConstraint(generator))


def with_diameter(min_val: int, max_val: int | None = None) -> Callable[[F], F]:
    """Constrain the tree diameter (longest path length).

    Args:
        min_val: Minimum diameter (or exact diameter if max_val is None).
        max_val: Maximum diameter.

    Example:
        @with_diameter(5, 8)  # Diameter between 5 and 8
        def tree_with_diameter():
            return Tree(n=10)
    """
    if max_val is None:
        max_val = min_val
    return add_constraint(DiameterConstraint(min_val, max_val))


def with_centroid(count: int = 1) -> Callable[[F], F]:
    """Constrain the number of tree centroids.

    A tree has 1 centroid if there's a single node that minimizes max subtree size,
    or 2 centroids if two adjacent nodes tie for this property.

    Args:
        count: Number of centroids (1 or 2).

    Example:
        @with_centroid(1)  # Single centroid
        def balanced_tree():
            return Tree(n=10)
    """
    return add_constraint(CentroidConstraint(count))


def with_depth(min_val: int, max_val: int | None = None) -> Callable[[F], F]:
    """Constrain the tree depth (max distance from root to any leaf).

    Args:
        min_val: Minimum depth (or exact depth if max_val is None).
        max_val: Maximum depth.

    Example:
        @with_depth(3, 5)  # Depth between 3 and 5
        def shallow_tree():
            return Tree(n=10)
    """
    if max_val is None:
        max_val = min_val
    return add_constraint(DepthConstraint(min_val, max_val))
