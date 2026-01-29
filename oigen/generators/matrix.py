"""
Matrix generator for 2D arrays and mazes.
"""

from dataclasses import dataclass
from random import Random
from typing import Any

from oigen.errors import ConstraintError
from oigen.generators import BaseGenerator


@dataclass
class MatrixData:
    """Generated matrix data.

    Attributes:
        rows: Number of rows.
        cols: Number of columns.
        data: 2D list of values.
    """
    rows: int
    cols: int
    data: list[list[Any]]

    def __str__(self) -> str:
        """Format matrix for output."""
        lines = [f"{self.rows} {self.cols}"]
        for row in self.data:
            if all(isinstance(x, str) and len(x) == 1 for x in row):
                # Character matrix (maze) - no spaces
                lines.append("".join(str(x) for x in row))
            else:
                # Numeric matrix - space separated
                lines.append(" ".join(str(x) for x in row))
        return "\n".join(lines)


class Matrix(BaseGenerator):
    """Generator for 2D matrices.

    Creates numeric matrices or character-based mazes depending on constraints.

    Args:
        rows: Number of rows (int or tuple for range).
        cols: Number of columns (int or tuple for range).
        element: Generator for each element (default: None for maze mode).

    Example:
        >>> gen = Matrix(rows=5, cols=5, element=Int(1, 10))  # Numeric matrix
        >>> gen = Matrix(rows=10, cols=10)  # For maze with decorators
    """

    def __init__(
        self,
        rows: int | tuple[int, int] = 10,
        cols: int | tuple[int, int] = 10,
        element: BaseGenerator | None = None,
    ):
        self.rows = rows
        self.cols = cols
        self.element = element
        self._constraint_registry = None
        self.validate()

    def validate(self) -> None:
        for name, dim in [("rows", self.rows), ("cols", self.cols)]:
            if isinstance(dim, tuple):
                min_val, max_val = dim
                if min_val < 1:
                    raise ConstraintError(
                        f"Matrix: {name} min ({min_val}) must be >= 1",
                        suggestion="Use a positive minimum",
                    )
                if min_val > max_val:
                    raise ConstraintError(
                        f"Matrix: {name} min ({min_val}) must be <= max ({max_val})",
                        suggestion="Swap the min and max values",
                    )
            elif isinstance(dim, int):
                if dim < 1:
                    raise ConstraintError(
                        f"Matrix: {name} ({dim}) must be >= 1",
                        suggestion="Use a positive dimension",
                    )

        if self.element is not None and not isinstance(self.element, BaseGenerator):
            raise ConstraintError(
                f"Matrix: element must be a generator, got {type(self.element).__name__}",
                suggestion="Use a generator like Int(1, 10)",
            )

    def _get_dim(self, dim: int | tuple[int, int], rng: Random) -> int:
        """Resolve actual dimension."""
        if isinstance(dim, tuple):
            return rng.randint(dim[0], dim[1])
        return dim

    def _get_context(self) -> dict[str, Any]:
        """Get constraint context if available."""
        if self._constraint_registry is not None:
            return self._constraint_registry.apply_all(self)
        return {}

    def _generate_maze(
        self,
        rows: int,
        cols: int,
        path_char: str,
        wall_char: str,
        path_start: tuple[int, int] | None,
        path_end: tuple[int, int] | None,
        border_char: str | None,
        rng: Random,
    ) -> list[list[str]]:
        """Generate a maze with optional guaranteed path."""
        # Start with all walls
        maze = [[wall_char for _ in range(cols)] for _ in range(rows)]

        # Apply border if specified
        if border_char:
            for c in range(cols):
                maze[0][c] = border_char
                maze[rows - 1][c] = border_char
            for r in range(rows):
                maze[r][0] = border_char
                maze[r][cols - 1] = border_char

        # Generate path using DFS
        if path_start and path_end:
            # Ensure path between start and end
            sr, sc = path_start
            er, ec = path_end

            # Simple path generation: carve a path
            visited = set()
            self._carve_path(maze, sr, sc, er, ec, path_char, visited, rng)

        # Add some random passages
        wall_prob = 0.3  # Probability of keeping a wall
        border_offset = 1 if border_char else 0

        for r in range(border_offset, rows - border_offset):
            for c in range(border_offset, cols - border_offset):
                if maze[r][c] == wall_char and rng.random() > wall_prob:
                    maze[r][c] = path_char

        return maze

    def _carve_path(
        self,
        maze: list[list[str]],
        sr: int, sc: int,
        er: int, ec: int,
        path_char: str,
        visited: set[tuple[int, int]],
        rng: Random,
    ) -> bool:
        """Carve a path from start to end using DFS."""
        rows, cols = len(maze), len(maze[0])

        # BFS to find path
        from collections import deque

        queue = deque([(sr, sc, [(sr, sc)])])
        visited = {(sr, sc)}

        while queue:
            r, c, path = queue.popleft()

            if r == er and c == ec:
                # Found path, carve it
                for pr, pc in path:
                    maze[pr][pc] = path_char
                return True

            # Try all directions
            directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
            rng.shuffle(directions)

            for dr, dc in directions:
                nr, nc = r + dr, c + dc
                if 0 <= nr < rows and 0 <= nc < cols and (nr, nc) not in visited:
                    visited.add((nr, nc))
                    queue.append((nr, nc, path + [(nr, nc)]))

        return False

    def _apply_row_col_constraints(
        self,
        data: list[list[Any]],
        context: dict[str, Any],
        rng: Random,
    ) -> list[list[Any]]:
        """Apply row/column sum/product constraints."""
        rows, cols = len(data), len(data[0])

        # Row sum constraint
        if "row_sum_max" in context:
            max_sum = context["row_sum_max"]
            for r in range(rows):
                while sum(data[r]) > max_sum:
                    # Reduce a random element
                    c = rng.randint(0, cols - 1)
                    if data[r][c] > 1:
                        data[r][c] -= 1

        # Column sum constraint
        if "col_sum_max" in context:
            max_sum = context["col_sum_max"]
            for c in range(cols):
                col_sum = sum(data[r][c] for r in range(rows))
                while col_sum > max_sum:
                    r = rng.randint(0, rows - 1)
                    if data[r][c] > 1:
                        data[r][c] -= 1
                        col_sum -= 1

        return data

    def generate(self, rng: Random) -> MatrixData:
        context = self._get_context()

        # Resolve dimensions
        rows = self._get_dim(self.rows, rng)
        cols = self._get_dim(self.cols, rng)

        # Check for maze mode
        if "maze" in context:
            path_char, wall_char = context["maze"]
            path_start = context.get("path_start")
            path_end = context.get("path_end")
            border_char = context.get("border")

            data = self._generate_maze(
                rows, cols, path_char, wall_char,
                path_start, path_end, border_char, rng
            )
            return MatrixData(rows=rows, cols=cols, data=data)

        # Numeric matrix mode
        if self.element is None:
            raise ConstraintError(
                "Matrix: element generator required for numeric matrix",
                suggestion="Provide element=Int(1, 10) or use @as_maze decorator",
            )

        data = [[self.element.generate(rng) for _ in range(cols)] for _ in range(rows)]

        # Apply constraints
        data = self._apply_row_col_constraints(data, context, rng)

        # Apply coordinate constraint
        if "coord_constraint" in context:
            predicate = context["coord_constraint"]
            for r in range(rows):
                for c in range(cols):
                    # Regenerate until constraint is satisfied
                    for _ in range(100):
                        if predicate(r, c, data[r][c]):
                            break
                        data[r][c] = self.element.generate(rng)

        return MatrixData(rows=rows, cols=cols, data=data)

    def __repr__(self) -> str:
        if self.element:
            return f"Matrix(rows={self.rows!r}, cols={self.cols!r}, element={self.element!r})"
        return f"Matrix(rows={self.rows!r}, cols={self.cols!r})"
