"""
Tests for oigen.generators.sequence module.
"""

from random import Random

import pytest

from oigen.errors import ConstraintError
from oigen.generators import Int
from oigen.generators.sequence import Sequence


class TestSequence:
    def test_fixed_length_generation(self, rng):
        gen = Sequence(Int(1, 10), length=5)
        result = gen.generate(rng)
        assert isinstance(result, list)
        assert len(result) == 5

    def test_fixed_length_elements(self, rng):
        gen = Sequence(Int(1, 10), length=5)
        result = gen.generate(rng)
        for elem in result:
            assert isinstance(elem, int)
            assert 1 <= elem <= 10

    def test_variable_length_generation(self, rng):
        gen = Sequence(Int(1, 10), length=(3, 7))
        for _ in range(100):
            result = gen.generate(rng)
            assert 3 <= len(result) <= 7

    def test_deterministic_generation(self):
        gen = Sequence(Int(1, 100), length=5)
        rng1 = Random(42)
        rng2 = Random(42)
        assert gen.generate(rng1) == gen.generate(rng2)

    def test_empty_sequence(self, rng):
        gen = Sequence(Int(1, 10), length=0)
        result = gen.generate(rng)
        assert result == []

    def test_single_element(self, rng):
        gen = Sequence(Int(1, 10), length=1)
        result = gen.generate(rng)
        assert len(result) == 1

    def test_default_length(self):
        gen = Sequence(Int(1, 10))
        assert gen.length == 10

    def test_validate_non_generator_element_raises(self):
        with pytest.raises(ConstraintError) as exc_info:
            Sequence(42, length=5)
        assert "must be a generator" in str(exc_info.value)

    def test_validate_string_element_raises(self):
        with pytest.raises(ConstraintError) as exc_info:
            Sequence("not a generator", length=5)
        assert "must be a generator" in str(exc_info.value)

    def test_validate_negative_length_raises(self):
        with pytest.raises(ConstraintError) as exc_info:
            Sequence(Int(1, 10), length=-1)
        assert "negative" in str(exc_info.value)

    def test_validate_tuple_min_greater_than_max_raises(self):
        with pytest.raises(ConstraintError) as exc_info:
            Sequence(Int(1, 10), length=(10, 5))
        assert "min length" in str(exc_info.value)
        assert "max length" in str(exc_info.value)

    def test_validate_tuple_negative_min_raises(self):
        with pytest.raises(ConstraintError) as exc_info:
            Sequence(Int(1, 10), length=(-1, 5))
        assert "negative" in str(exc_info.value)

    def test_validate_invalid_length_type_raises(self):
        with pytest.raises(ConstraintError) as exc_info:
            Sequence(Int(1, 10), length="five")
        assert "int or tuple" in str(exc_info.value)

    def test_repr(self):
        gen = Sequence(Int(1, 10), length=5)
        r = repr(gen)
        assert "Sequence" in r
        assert "Int" in r
        assert "5" in r

    def test_repr_variable_length(self):
        gen = Sequence(Int(1, 10), length=(3, 7))
        r = repr(gen)
        assert "(3, 7)" in r
