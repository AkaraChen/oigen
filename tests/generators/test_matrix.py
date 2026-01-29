"""
Tests for oigen.generators.matrix module.
"""

from random import Random

import pytest

from oigen.errors import ConstraintError
from oigen.generators import Int
from oigen.generators.matrix import Matrix, MatrixData
from oigen.generators.primitives import Char


class TestMatrixData:
    def test_str_format_numeric(self):
        data = MatrixData(rows=2, cols=3, data=[[1, 2, 3], [4, 5, 6]])
        s = str(data)
        lines = s.strip().split("\n")
        assert lines[0] == "2 3"  # rows cols
        assert lines[1] == "1 2 3"
        assert lines[2] == "4 5 6"

    def test_str_format_character(self):
        data = MatrixData(rows=2, cols=3, data=[["a", "b", "c"], ["d", "e", "f"]])
        s = str(data)
        lines = s.strip().split("\n")
        assert lines[0] == "2 3"
        assert lines[1] == "abc"  # No spaces for characters
        assert lines[2] == "def"

    def test_str_format_single_cell(self):
        data = MatrixData(rows=1, cols=1, data=[[42]])
        s = str(data)
        lines = s.strip().split("\n")
        assert lines[0] == "1 1"
        assert lines[1] == "42"


class TestMatrix:
    def test_generate_fixed_dimensions(self, rng):
        gen = Matrix(rows=3, cols=4, element=Int(0, 9))
        result = gen.generate(rng)
        assert result.rows == 3
        assert result.cols == 4
        assert len(result.data) == 3
        assert all(len(row) == 4 for row in result.data)

    def test_generate_variable_rows(self, rng):
        gen = Matrix(rows=(2, 5), cols=3, element=Int(0, 9))
        for _ in range(100):
            result = gen.generate(rng)
            assert 2 <= result.rows <= 5
            assert result.cols == 3

    def test_generate_variable_cols(self, rng):
        gen = Matrix(rows=3, cols=(2, 5), element=Int(0, 9))
        for _ in range(100):
            result = gen.generate(rng)
            assert result.rows == 3
            assert 2 <= result.cols <= 5

    def test_generate_variable_both(self, rng):
        gen = Matrix(rows=(2, 4), cols=(3, 6), element=Int(0, 9))
        for _ in range(100):
            result = gen.generate(rng)
            assert 2 <= result.rows <= 4
            assert 3 <= result.cols <= 6

    def test_generate_element_values(self, rng):
        gen = Matrix(rows=3, cols=3, element=Int(1, 5))
        result = gen.generate(rng)
        for row in result.data:
            for val in row:
                assert 1 <= val <= 5

    def test_generate_deterministic(self):
        gen = Matrix(rows=3, cols=3, element=Int(0, 9))
        rng1 = Random(42)
        rng2 = Random(42)
        result1 = gen.generate(rng1)
        result2 = gen.generate(rng2)
        assert result1.data == result2.data

    def test_generate_char_matrix(self, rng):
        gen = Matrix(rows=2, cols=3, element=Char(charset="ab"))
        result = gen.generate(rng)
        for row in result.data:
            for val in row:
                assert val in "ab"

    def test_generate_without_element_raises(self, rng):
        gen = Matrix(rows=3, cols=3)  # No element
        with pytest.raises(ConstraintError) as exc_info:
            gen.generate(rng)
        assert "element generator required" in str(exc_info.value)

    def test_validate_rows_less_than_1_raises(self):
        with pytest.raises(ConstraintError) as exc_info:
            Matrix(rows=0, cols=3, element=Int(0, 9))
        assert "rows" in str(exc_info.value)
        assert ">= 1" in str(exc_info.value)

    def test_validate_cols_less_than_1_raises(self):
        with pytest.raises(ConstraintError) as exc_info:
            Matrix(rows=3, cols=0, element=Int(0, 9))
        assert "cols" in str(exc_info.value)

    def test_validate_tuple_min_greater_than_max_rows(self):
        with pytest.raises(ConstraintError) as exc_info:
            Matrix(rows=(5, 2), cols=3, element=Int(0, 9))
        assert "rows" in str(exc_info.value)
        assert "min" in str(exc_info.value)

    def test_validate_tuple_min_greater_than_max_cols(self):
        with pytest.raises(ConstraintError) as exc_info:
            Matrix(rows=3, cols=(5, 2), element=Int(0, 9))
        assert "cols" in str(exc_info.value)

    def test_validate_tuple_min_less_than_1(self):
        with pytest.raises(ConstraintError) as exc_info:
            Matrix(rows=(0, 5), cols=3, element=Int(0, 9))
        assert "rows" in str(exc_info.value)
        assert ">= 1" in str(exc_info.value)

    def test_validate_element_not_generator_raises(self):
        with pytest.raises(ConstraintError) as exc_info:
            Matrix(rows=3, cols=3, element=42)
        assert "element" in str(exc_info.value)
        assert "generator" in str(exc_info.value)

    def test_repr_with_element(self):
        gen = Matrix(rows=3, cols=4, element=Int(0, 9))
        r = repr(gen)
        assert "Matrix" in r
        assert "rows=3" in r
        assert "cols=4" in r
        assert "Int" in r

    def test_repr_without_element(self):
        gen = Matrix(rows=3, cols=4)
        r = repr(gen)
        assert "Matrix" in r
        assert "rows=3" in r
        assert "cols=4" in r


class TestMatrixAdvancedFeatures:
    """Tests for advanced matrix generation with constraints."""

    def test_generate_maze_basic(self, rng):
        gen = Matrix(rows=5, cols=5)
        gen._constraint_registry = type("FakeRegistry", (), {
            "apply_all": lambda self, g: {"maze": (".", "#")}
        })()
        result = gen.generate(rng)
        assert result.rows == 5
        assert result.cols == 5
        for row in result.data:
            for cell in row:
                assert cell in ".#"

    def test_generate_maze_with_border(self, rng):
        gen = Matrix(rows=5, cols=5)
        gen._constraint_registry = type("FakeRegistry", (), {
            "apply_all": lambda self, g: {"maze": (".", "#"), "border": "X"}
        })()
        result = gen.generate(rng)
        # Check border
        for cell in result.data[0]:
            assert cell == "X"
        for cell in result.data[-1]:
            assert cell == "X"
        for row in result.data:
            assert row[0] == "X"
            assert row[-1] == "X"

    def test_generate_maze_with_path(self, rng):
        gen = Matrix(rows=5, cols=5)
        gen._constraint_registry = type("FakeRegistry", (), {
            "apply_all": lambda self, g: {
                "maze": (".", "#"),
                "path_start": (0, 0),
                "path_end": (4, 4)
            }
        })()
        result = gen.generate(rng)
        # Start and end should be path characters
        assert result.data[0][0] == "."
        assert result.data[4][4] == "."

    def test_generate_with_row_sum_constraint(self, rng):
        gen = Matrix(rows=3, cols=3, element=Int(1, 10))
        gen._constraint_registry = type("FakeRegistry", (), {
            "apply_all": lambda self, g: {"row_sum_max": 15}
        })()
        result = gen.generate(rng)
        for row in result.data:
            assert sum(row) <= 15

    def test_generate_with_col_sum_constraint(self, rng):
        gen = Matrix(rows=3, cols=3, element=Int(1, 5))
        gen._constraint_registry = type("FakeRegistry", (), {
            "apply_all": lambda self, g: {"col_sum_max": 10}
        })()
        result = gen.generate(rng)
        for c in range(3):
            col_sum = sum(result.data[r][c] for r in range(3))
            assert col_sum <= 10

    def test_generate_with_coord_constraint(self, rng):
        gen = Matrix(rows=3, cols=3, element=Int(1, 100))
        # Constraint: diagonal elements must be > 50
        gen._constraint_registry = type("FakeRegistry", (), {
            "apply_all": lambda self, g: {
                "coord_constraint": lambda r, c, v: r != c or v > 50
            }
        })()
        result = gen.generate(rng)
        for i in range(3):
            assert result.data[i][i] > 50
