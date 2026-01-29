"""
Tests for oigen.decorators.matrix module.
"""

import pytest

from oigen.decorators.base import ConstraintRegistry, get_constraints
from oigen.decorators.matrix import (
    BorderConstraint,
    ColOperatorConstraint,
    ColProductConstraint,
    ColSumConstraint,
    CoordConstraint,
    MazeConstraint,
    PathBetweenConstraint,
    RowOperatorConstraint,
    RowProductConstraint,
    RowSumConstraint,
    as_maze,
    col_product_max,
    col_sum_max,
    row_product_max,
    row_sum_max,
    with_border,
    with_col_operator,
    with_coord_constraint,
    with_path_between,
    with_row_operator,
)
from oigen.errors import ConstraintError
from oigen.generators import Int
from oigen.generators.matrix import Matrix


class TestMazeConstraint:
    def test_validate_valid(self):
        c = MazeConstraint(path=".", wall="#")
        c.validate(Matrix(rows=10, cols=10), ConstraintRegistry())

    def test_validate_same_chars(self):
        c = MazeConstraint(path="#", wall="#")
        with pytest.raises(ConstraintError) as exc_info:
            c.validate(Matrix(rows=10, cols=10), ConstraintRegistry())
        assert "different" in str(exc_info.value)

    def test_apply(self):
        c = MazeConstraint(path=".", wall="#")
        context = {}
        c.apply(Matrix(rows=10, cols=10), context)
        assert context["maze"] == (".", "#")


class TestPathBetweenConstraint:
    def test_validate_valid(self):
        c = PathBetweenConstraint(start=(0, 0), end=(9, 9))
        registry = ConstraintRegistry()
        registry.add(MazeConstraint(path=".", wall="#"))
        c.validate(Matrix(rows=10, cols=10), registry)

    def test_validate_no_maze(self):
        c = PathBetweenConstraint(start=(0, 0), end=(9, 9))
        with pytest.raises(ConstraintError) as exc_info:
            c.validate(Matrix(rows=10, cols=10), ConstraintRegistry())
        assert "requires @as_maze" in str(exc_info.value)

    def test_validate_invalid_tuple_length(self):
        c = PathBetweenConstraint(start=(0, 0, 0), end=(9, 9))  # type: ignore
        registry = ConstraintRegistry()
        registry.add(MazeConstraint(path=".", wall="#"))
        with pytest.raises(ConstraintError) as exc_info:
            c.validate(Matrix(rows=10, cols=10), registry)
        assert "tuple" in str(exc_info.value)

    def test_validate_negative_coord(self):
        c = PathBetweenConstraint(start=(-1, 0), end=(9, 9))
        registry = ConstraintRegistry()
        registry.add(MazeConstraint(path=".", wall="#"))
        with pytest.raises(ConstraintError) as exc_info:
            c.validate(Matrix(rows=10, cols=10), registry)
        assert "negative" in str(exc_info.value)

    def test_apply(self):
        c = PathBetweenConstraint(start=(0, 0), end=(9, 9))
        context = {}
        c.apply(Matrix(rows=10, cols=10), context)
        assert context["path_start"] == (0, 0)
        assert context["path_end"] == (9, 9)


class TestBorderConstraint:
    def test_validate_valid(self):
        c = BorderConstraint(symbol="#")
        c.validate(Matrix(rows=10, cols=10), ConstraintRegistry())

    def test_validate_not_single_char(self):
        c = BorderConstraint(symbol="##")
        with pytest.raises(ConstraintError) as exc_info:
            c.validate(Matrix(rows=10, cols=10), ConstraintRegistry())
        assert "single character" in str(exc_info.value)

    def test_apply(self):
        c = BorderConstraint(symbol="#")
        context = {}
        c.apply(Matrix(rows=10, cols=10), context)
        assert context["border"] == "#"


class TestCoordConstraint:
    def test_validate_valid(self):
        c = CoordConstraint(predicate=lambda r, c, v: True)
        c.validate(Matrix(rows=5, cols=5, element=Int(1, 10)), ConstraintRegistry())

    def test_validate_not_callable(self):
        c = CoordConstraint(predicate="not callable")  # type: ignore
        with pytest.raises(ConstraintError) as exc_info:
            c.validate(Matrix(rows=5, cols=5, element=Int(1, 10)), ConstraintRegistry())
        assert "callable" in str(exc_info.value)

    def test_apply(self):
        def pred(r, c, v):
            return r + c < 5
        c = CoordConstraint(predicate=pred)
        context = {}
        c.apply(Matrix(rows=5, cols=5, element=Int(1, 10)), context)
        assert context["coord_constraint"] is pred


class TestRowSumConstraint:
    def test_validate_valid(self):
        c = RowSumConstraint(max_val=100)
        c.validate(Matrix(rows=5, cols=5, element=Int(1, 10)), ConstraintRegistry())

    def test_validate_negative(self):
        c = RowSumConstraint(max_val=-1)
        with pytest.raises(ConstraintError) as exc_info:
            c.validate(Matrix(rows=5, cols=5, element=Int(1, 10)), ConstraintRegistry())
        assert "negative" in str(exc_info.value)

    def test_apply(self):
        c = RowSumConstraint(max_val=100)
        context = {}
        c.apply(Matrix(rows=5, cols=5, element=Int(1, 10)), context)
        assert context["row_sum_max"] == 100


class TestColSumConstraint:
    def test_validate_valid(self):
        c = ColSumConstraint(max_val=100)
        c.validate(Matrix(rows=5, cols=5, element=Int(1, 10)), ConstraintRegistry())

    def test_validate_negative(self):
        c = ColSumConstraint(max_val=-1)
        with pytest.raises(ConstraintError) as exc_info:
            c.validate(Matrix(rows=5, cols=5, element=Int(1, 10)), ConstraintRegistry())
        assert "negative" in str(exc_info.value)

    def test_apply(self):
        c = ColSumConstraint(max_val=100)
        context = {}
        c.apply(Matrix(rows=5, cols=5, element=Int(1, 10)), context)
        assert context["col_sum_max"] == 100


class TestRowProductConstraint:
    def test_validate_valid(self):
        c = RowProductConstraint(max_val=1000)
        c.validate(Matrix(rows=5, cols=5, element=Int(1, 5)), ConstraintRegistry())

    def test_validate_not_positive(self):
        c = RowProductConstraint(max_val=0)
        with pytest.raises(ConstraintError) as exc_info:
            c.validate(Matrix(rows=5, cols=5, element=Int(1, 5)), ConstraintRegistry())
        assert "positive" in str(exc_info.value)

    def test_apply(self):
        c = RowProductConstraint(max_val=1000)
        context = {}
        c.apply(Matrix(rows=5, cols=5, element=Int(1, 5)), context)
        assert context["row_product_max"] == 1000


class TestColProductConstraint:
    def test_validate_valid(self):
        c = ColProductConstraint(max_val=1000)
        c.validate(Matrix(rows=5, cols=5, element=Int(1, 5)), ConstraintRegistry())

    def test_validate_not_positive(self):
        c = ColProductConstraint(max_val=-10)
        with pytest.raises(ConstraintError) as exc_info:
            c.validate(Matrix(rows=5, cols=5, element=Int(1, 5)), ConstraintRegistry())
        assert "positive" in str(exc_info.value)

    def test_apply(self):
        c = ColProductConstraint(max_val=1000)
        context = {}
        c.apply(Matrix(rows=5, cols=5, element=Int(1, 5)), context)
        assert context["col_product_max"] == 1000


class TestRowOperatorConstraint:
    def test_validate_valid(self):
        c = RowOperatorConstraint(op=sum, max_val=100)
        c.validate(Matrix(rows=5, cols=5, element=Int(1, 10)), ConstraintRegistry())

    def test_validate_not_callable(self):
        c = RowOperatorConstraint(op="not callable", max_val=100)  # type: ignore
        with pytest.raises(ConstraintError) as exc_info:
            c.validate(Matrix(rows=5, cols=5, element=Int(1, 10)), ConstraintRegistry())
        assert "callable" in str(exc_info.value)

    def test_apply(self):
        c = RowOperatorConstraint(op=sum, max_val=100)
        context = {}
        c.apply(Matrix(rows=5, cols=5, element=Int(1, 10)), context)
        assert context["row_operator"] == (sum, 100)


class TestColOperatorConstraint:
    def test_validate_valid(self):
        c = ColOperatorConstraint(op=sum, max_val=100)
        c.validate(Matrix(rows=5, cols=5, element=Int(1, 10)), ConstraintRegistry())

    def test_validate_not_callable(self):
        c = ColOperatorConstraint(op=42, max_val=100)  # type: ignore
        with pytest.raises(ConstraintError) as exc_info:
            c.validate(Matrix(rows=5, cols=5, element=Int(1, 10)), ConstraintRegistry())
        assert "callable" in str(exc_info.value)

    def test_apply(self):
        c = ColOperatorConstraint(op=sum, max_val=100)
        context = {}
        c.apply(Matrix(rows=5, cols=5, element=Int(1, 10)), context)
        assert context["col_operator"] == (sum, 100)


class TestDecoratorFunctions:
    def test_as_maze_default(self):
        @as_maze()
        def constrained():
            return Matrix(rows=10, cols=10)

        registry = get_constraints(constrained)
        assert registry is not None
        c = registry.get_one(MazeConstraint)
        assert c is not None
        assert c.path == "."
        assert c.wall == "#"

    def test_as_maze_custom(self):
        @as_maze(path=" ", wall="X")
        def constrained():
            return Matrix(rows=10, cols=10)

        registry = get_constraints(constrained)
        c = registry.get_one(MazeConstraint)
        assert c.path == " "
        assert c.wall == "X"

    def test_with_path_between(self):
        @with_path_between((0, 0), (9, 9))
        @as_maze()
        def constrained():
            return Matrix(rows=10, cols=10)

        registry = get_constraints(constrained)
        c = registry.get_one(PathBetweenConstraint)
        assert c is not None
        assert c.start == (0, 0)
        assert c.end == (9, 9)

    def test_with_border(self):
        @with_border("#")
        def constrained():
            return Matrix(rows=10, cols=10)

        registry = get_constraints(constrained)
        assert registry.has(BorderConstraint)

    def test_with_coord_constraint(self):
        def pred(r, c, v):
            return r + c < 5

        @with_coord_constraint(pred)
        def constrained():
            return Matrix(rows=5, cols=5, element=Int(1, 10))

        registry = get_constraints(constrained)
        assert registry.has(CoordConstraint)

    def test_row_sum_max(self):
        @row_sum_max(100)
        def constrained():
            return Matrix(rows=5, cols=5, element=Int(1, 30))

        registry = get_constraints(constrained)
        c = registry.get_one(RowSumConstraint)
        assert c is not None
        assert c.max_val == 100

    def test_col_sum_max(self):
        @col_sum_max(100)
        def constrained():
            return Matrix(rows=5, cols=5, element=Int(1, 30))

        registry = get_constraints(constrained)
        c = registry.get_one(ColSumConstraint)
        assert c is not None
        assert c.max_val == 100

    def test_row_product_max(self):
        @row_product_max(1000)
        def constrained():
            return Matrix(rows=5, cols=5, element=Int(1, 5))

        registry = get_constraints(constrained)
        c = registry.get_one(RowProductConstraint)
        assert c is not None
        assert c.max_val == 1000

    def test_col_product_max(self):
        @col_product_max(1000)
        def constrained():
            return Matrix(rows=5, cols=5, element=Int(1, 5))

        registry = get_constraints(constrained)
        c = registry.get_one(ColProductConstraint)
        assert c is not None
        assert c.max_val == 1000

    def test_with_row_operator(self):
        @with_row_operator(sum, max_val=100)
        def constrained():
            return Matrix(rows=5, cols=5, element=Int(1, 10))

        registry = get_constraints(constrained)
        assert registry.has(RowOperatorConstraint)

    def test_with_col_operator(self):
        @with_col_operator(sum, max_val=100)
        def constrained():
            return Matrix(rows=5, cols=5, element=Int(1, 10))

        registry = get_constraints(constrained)
        assert registry.has(ColOperatorConstraint)
