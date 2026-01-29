"""
Matrix constraint decorators.
"""

from dataclasses import dataclass
from typing import Any, Callable, TypeVar

from oigen.decorators.base import Constraint, ConstraintRegistry, add_constraint
from oigen.errors import ConstraintError
from oigen.generators import BaseGenerator


F = TypeVar("F", bound=Callable[..., BaseGenerator])


# ============================================================================
# Matrix Constraints
# ============================================================================


@dataclass
class MazeConstraint(Constraint):
    """Constraint for maze mode."""

    path: str
    wall: str

    def validate(self, generator: BaseGenerator, registry: ConstraintRegistry) -> None:
        if self.path == self.wall:
            raise ConstraintError(
                f"as_maze: path ('{self.path}') and wall ('{self.wall}') must be different",
                suggestion="Use different characters for path and wall",
            )

    def apply(self, generator: BaseGenerator, context: dict[str, Any]) -> None:
        context["maze"] = (self.path, self.wall)

    @property
    def priority(self) -> int:
        return 5


@dataclass
class PathBetweenConstraint(Constraint):
    """Constraint for guaranteed path in maze."""

    start: tuple[int, int]
    end: tuple[int, int]

    def validate(self, generator: BaseGenerator, registry: ConstraintRegistry) -> None:
        # Check maze mode is enabled
        if not registry.has(MazeConstraint):
            raise ConstraintError(
                "with_path_between: requires @as_maze decorator",
                suggestion="Add @as_maze() before this decorator",
            )

        for name, coord in [("start", self.start), ("end", self.end)]:
            if len(coord) != 2:
                raise ConstraintError(
                    f"with_path_between: {name} must be (row, col) tuple",
                    suggestion="Use format like (0, 0) for top-left",
                )
            r, c = coord
            if r < 0 or c < 0:
                raise ConstraintError(
                    f"with_path_between: {name} ({r}, {c}) has negative coordinate",
                    suggestion="Use non-negative coordinates",
                )

    def apply(self, generator: BaseGenerator, context: dict[str, Any]) -> None:
        context["path_start"] = self.start
        context["path_end"] = self.end

    @property
    def priority(self) -> int:
        return 10


@dataclass
class BorderConstraint(Constraint):
    """Constraint for matrix border."""

    symbol: str

    def validate(self, generator: BaseGenerator, registry: ConstraintRegistry) -> None:
        if len(self.symbol) != 1:
            raise ConstraintError(
                f"with_border: symbol must be single character, got '{self.symbol}'",
                suggestion="Use a single character like '#' or '*'",
            )

    def apply(self, generator: BaseGenerator, context: dict[str, Any]) -> None:
        context["border"] = self.symbol

    @property
    def priority(self) -> int:
        return 5


@dataclass
class CoordConstraint(Constraint):
    """Constraint based on coordinates."""

    predicate: Callable[[int, int, Any], bool]

    def validate(self, generator: BaseGenerator, registry: ConstraintRegistry) -> None:
        if not callable(self.predicate):
            raise ConstraintError(
                "with_coord_constraint: predicate must be callable",
                suggestion="Use a function like lambda r, c, v: r + c < 5 or v > 3",
            )

    def apply(self, generator: BaseGenerator, context: dict[str, Any]) -> None:
        context["coord_constraint"] = self.predicate

    @property
    def priority(self) -> int:
        return 50


@dataclass
class RowSumConstraint(Constraint):
    """Constraint for maximum row sum."""

    max_val: int | float

    def validate(self, generator: BaseGenerator, registry: ConstraintRegistry) -> None:
        if self.max_val < 0:
            raise ConstraintError(
                f"row_sum_max: max_val ({self.max_val}) cannot be negative",
                suggestion="Use a non-negative maximum",
            )

    def apply(self, generator: BaseGenerator, context: dict[str, Any]) -> None:
        context["row_sum_max"] = self.max_val

    @property
    def priority(self) -> int:
        return 30


@dataclass
class ColSumConstraint(Constraint):
    """Constraint for maximum column sum."""

    max_val: int | float

    def validate(self, generator: BaseGenerator, registry: ConstraintRegistry) -> None:
        if self.max_val < 0:
            raise ConstraintError(
                f"col_sum_max: max_val ({self.max_val}) cannot be negative",
                suggestion="Use a non-negative maximum",
            )

    def apply(self, generator: BaseGenerator, context: dict[str, Any]) -> None:
        context["col_sum_max"] = self.max_val

    @property
    def priority(self) -> int:
        return 30


@dataclass
class RowProductConstraint(Constraint):
    """Constraint for maximum row product."""

    max_val: int | float

    def validate(self, generator: BaseGenerator, registry: ConstraintRegistry) -> None:
        if self.max_val <= 0:
            raise ConstraintError(
                f"row_product_max: max_val ({self.max_val}) must be positive",
                suggestion="Use a positive maximum",
            )

    def apply(self, generator: BaseGenerator, context: dict[str, Any]) -> None:
        context["row_product_max"] = self.max_val

    @property
    def priority(self) -> int:
        return 30


@dataclass
class ColProductConstraint(Constraint):
    """Constraint for maximum column product."""

    max_val: int | float

    def validate(self, generator: BaseGenerator, registry: ConstraintRegistry) -> None:
        if self.max_val <= 0:
            raise ConstraintError(
                f"col_product_max: max_val ({self.max_val}) must be positive",
                suggestion="Use a positive maximum",
            )

    def apply(self, generator: BaseGenerator, context: dict[str, Any]) -> None:
        context["col_product_max"] = self.max_val

    @property
    def priority(self) -> int:
        return 30


@dataclass
class RowOperatorConstraint(Constraint):
    """Constraint for custom row operator."""

    op: Callable[[list[Any]], Any]
    max_val: int | float

    def validate(self, generator: BaseGenerator, registry: ConstraintRegistry) -> None:
        if not callable(self.op):
            raise ConstraintError(
                "with_row_operator: op must be callable",
                suggestion="Use a function like sum or lambda row: max(row)",
            )

    def apply(self, generator: BaseGenerator, context: dict[str, Any]) -> None:
        context["row_operator"] = (self.op, self.max_val)

    @property
    def priority(self) -> int:
        return 40


@dataclass
class ColOperatorConstraint(Constraint):
    """Constraint for custom column operator."""

    op: Callable[[list[Any]], Any]
    max_val: int | float

    def validate(self, generator: BaseGenerator, registry: ConstraintRegistry) -> None:
        if not callable(self.op):
            raise ConstraintError(
                "with_col_operator: op must be callable",
                suggestion="Use a function like sum or lambda col: max(col)",
            )

    def apply(self, generator: BaseGenerator, context: dict[str, Any]) -> None:
        context["col_operator"] = (self.op, self.max_val)

    @property
    def priority(self) -> int:
        return 40


# ============================================================================
# Decorator Functions
# ============================================================================


def as_maze(path: str = ".", wall: str = "#") -> Callable[[F], F]:
    """Enable maze mode with specified path and wall characters.

    Args:
        path: Character for passable cells (default ".").
        wall: Character for walls (default "#").

    Example:
        @as_maze()
        def simple_maze():
            return Matrix(rows=10, cols=10)

        @as_maze(path=" ", wall="█")
        def unicode_maze():
            return Matrix(rows=10, cols=10)
    """
    return add_constraint(MazeConstraint(path, wall))


def with_path_between(
    start: tuple[int, int],
    end: tuple[int, int],
) -> Callable[[F], F]:
    """Guarantee a path exists between two points in the maze.

    Args:
        start: Starting coordinate (row, col), 0-indexed.
        end: Ending coordinate (row, col), 0-indexed.

    Example:
        @with_path_between((0, 0), (9, 9))
        @as_maze()
        def solvable_maze():
            return Matrix(rows=10, cols=10)
    """
    return add_constraint(PathBetweenConstraint(start, end))


def with_border(symbol: str) -> Callable[[F], F]:
    """Add a border around the matrix with the specified symbol.

    Args:
        symbol: Single character for border.

    Example:
        @with_border("#")
        @as_maze()
        def bordered_maze():
            return Matrix(rows=10, cols=10)
    """
    return add_constraint(BorderConstraint(symbol))


def with_coord_constraint(
    predicate: Callable[[int, int, Any], bool],
) -> Callable[[F], F]:
    """Add a constraint based on coordinates and value.

    The predicate receives (row, col, value) and should return True if valid.

    Args:
        predicate: Function (row, col, value) -> bool.

    Example:
        @with_coord_constraint(lambda r, c, v: r + c < 5 or v > 3)
        def constrained_matrix():
            return Matrix(rows=5, cols=5, element=Int(1, 10))
    """
    return add_constraint(CoordConstraint(predicate))


def row_sum_max(max_val: int | float) -> Callable[[F], F]:
    """Constrain maximum sum of each row.

    Args:
        max_val: Maximum allowed row sum.

    Example:
        @row_sum_max(100)
        def bounded_rows():
            return Matrix(rows=5, cols=5, element=Int(1, 30))
    """
    return add_constraint(RowSumConstraint(max_val))


def col_sum_max(max_val: int | float) -> Callable[[F], F]:
    """Constrain maximum sum of each column.

    Args:
        max_val: Maximum allowed column sum.

    Example:
        @col_sum_max(100)
        def bounded_cols():
            return Matrix(rows=5, cols=5, element=Int(1, 30))
    """
    return add_constraint(ColSumConstraint(max_val))


def row_product_max(max_val: int | float) -> Callable[[F], F]:
    """Constrain maximum product of each row.

    Args:
        max_val: Maximum allowed row product.

    Example:
        @row_product_max(1000)
        def bounded_row_product():
            return Matrix(rows=5, cols=5, element=Int(1, 5))
    """
    return add_constraint(RowProductConstraint(max_val))


def col_product_max(max_val: int | float) -> Callable[[F], F]:
    """Constrain maximum product of each column.

    Args:
        max_val: Maximum allowed column product.

    Example:
        @col_product_max(1000)
        def bounded_col_product():
            return Matrix(rows=5, cols=5, element=Int(1, 5))
    """
    return add_constraint(ColProductConstraint(max_val))


def with_row_operator(
    op: Callable[[list[Any]], Any],
    max_val: int | float,
) -> Callable[[F], F]:
    """Constrain rows using a custom operator.

    Args:
        op: Function that takes a row and returns a value.
        max_val: Maximum allowed value from operator.

    Example:
        @with_row_operator(lambda row: max(row) - min(row), max_val=10)
        def small_range_rows():
            return Matrix(rows=5, cols=5, element=Int(1, 100))
    """
    return add_constraint(RowOperatorConstraint(op, max_val))


def with_col_operator(
    op: Callable[[list[Any]], Any],
    max_val: int | float,
) -> Callable[[F], F]:
    """Constrain columns using a custom operator.

    Args:
        op: Function that takes a column and returns a value.
        max_val: Maximum allowed value from operator.

    Example:
        @with_col_operator(lambda col: max(col) - min(col), max_val=10)
        def small_range_cols():
            return Matrix(rows=5, cols=5, element=Int(1, 100))
    """
    return add_constraint(ColOperatorConstraint(op, max_val))
