"""
Tests for oigen.generators.primitives module.
"""

from random import Random
from string import ascii_lowercase

import pytest

from oigen.errors import ConstraintError
from oigen.generators.primitives import Int, Double, Char, Bool


class TestInt:
    def test_generate_within_range(self, rng):
        gen = Int(min_val=1, max_val=10)
        for _ in range(100):
            value = gen.generate(rng)
            assert 1 <= value <= 10

    def test_generate_deterministic(self):
        gen = Int(1, 100)
        rng1 = Random(42)
        rng2 = Random(42)
        assert gen.generate(rng1) == gen.generate(rng2)

    def test_min_equals_max(self, rng):
        gen = Int(min_val=5, max_val=5)
        for _ in range(10):
            assert gen.generate(rng) == 5

    def test_negative_range(self, rng):
        gen = Int(min_val=-10, max_val=-1)
        for _ in range(100):
            value = gen.generate(rng)
            assert -10 <= value <= -1

    def test_default_values(self, rng):
        gen = Int()
        assert gen.min_val == 0
        assert gen.max_val == 10**9

    def test_validate_min_greater_than_max_raises(self):
        with pytest.raises(ConstraintError) as exc_info:
            Int(min_val=10, max_val=1)
        assert "min" in str(exc_info.value)
        assert "max" in str(exc_info.value)

    def test_repr(self):
        gen = Int(1, 100)
        assert repr(gen) == "Int(1, 100)"


class TestDouble:
    def test_generate_within_range(self, rng):
        gen = Double(min_val=0.0, max_val=1.0)
        for _ in range(100):
            value = gen.generate(rng)
            assert 0.0 <= value <= 1.0

    def test_generate_deterministic(self):
        gen = Double(0.0, 10.0)
        rng1 = Random(42)
        rng2 = Random(42)
        assert gen.generate(rng1) == gen.generate(rng2)

    def test_respects_precision(self, rng):
        gen = Double(min_val=0.0, max_val=1.0, precision=2)
        for _ in range(100):
            value = gen.generate(rng)
            # Check that value has at most 2 decimal places
            assert value == round(value, 2)

    def test_precision_zero(self, rng):
        gen = Double(min_val=0.0, max_val=10.0, precision=0)
        for _ in range(100):
            value = gen.generate(rng)
            assert value == int(value)

    def test_default_precision(self, rng):
        gen = Double()
        assert gen.precision == 6

    def test_validate_min_greater_than_max_raises(self):
        with pytest.raises(ConstraintError) as exc_info:
            Double(min_val=10.0, max_val=1.0)
        assert "min" in str(exc_info.value)

    def test_validate_negative_precision_raises(self):
        with pytest.raises(ConstraintError) as exc_info:
            Double(min_val=0.0, max_val=1.0, precision=-1)
        assert "precision" in str(exc_info.value)

    def test_repr(self):
        gen = Double(0.0, 1.0, precision=2)
        assert "0.0" in repr(gen)
        assert "1.0" in repr(gen)
        assert "precision=2" in repr(gen)


class TestChar:
    def test_generate_from_default_charset(self, rng):
        gen = Char()
        for _ in range(100):
            value = gen.generate(rng)
            assert value in ascii_lowercase

    def test_generate_from_custom_charset(self, rng):
        gen = Char(charset="abc")
        for _ in range(100):
            value = gen.generate(rng)
            assert value in "abc"

    def test_generate_deterministic(self):
        gen = Char()
        rng1 = Random(42)
        rng2 = Random(42)
        assert gen.generate(rng1) == gen.generate(rng2)

    def test_single_char_charset(self, rng):
        gen = Char(charset="x")
        for _ in range(10):
            assert gen.generate(rng) == "x"

    def test_validate_empty_charset_raises(self):
        with pytest.raises(ConstraintError) as exc_info:
            Char(charset="")
        assert "charset" in str(exc_info.value)
        assert "empty" in str(exc_info.value)

    def test_repr_default(self):
        gen = Char()
        assert repr(gen) == "Char()"

    def test_repr_custom_charset(self):
        gen = Char(charset="abc")
        assert "abc" in repr(gen)


class TestBool:
    def test_generate_returns_bool(self, rng):
        gen = Bool()
        for _ in range(100):
            value = gen.generate(rng)
            assert isinstance(value, bool)

    def test_generate_deterministic(self):
        gen = Bool()
        rng1 = Random(42)
        rng2 = Random(42)
        assert gen.generate(rng1) == gen.generate(rng2)

    def test_true_prob_1_always_true(self, rng):
        gen = Bool(true_prob=1.0)
        for _ in range(100):
            assert gen.generate(rng) is True

    def test_true_prob_0_always_false(self, rng):
        gen = Bool(true_prob=0.0)
        for _ in range(100):
            assert gen.generate(rng) is False

    def test_default_probability(self):
        gen = Bool()
        assert gen.true_prob == 0.5

    def test_probability_distribution(self):
        gen = Bool(true_prob=0.8)
        rng = Random(42)

        true_count = sum(gen.generate(rng) for _ in range(1000))
        # With 0.8 probability, should be around 800 ± reasonable variance
        assert 700 < true_count < 900

    def test_validate_prob_greater_than_1_raises(self):
        with pytest.raises(ConstraintError) as exc_info:
            Bool(true_prob=1.5)
        assert "true_prob" in str(exc_info.value)
        assert "between 0 and 1" in str(exc_info.value)

    def test_validate_prob_less_than_0_raises(self):
        with pytest.raises(ConstraintError) as exc_info:
            Bool(true_prob=-0.1)
        assert "true_prob" in str(exc_info.value)

    def test_repr_default(self):
        gen = Bool()
        assert repr(gen) == "Bool()"

    def test_repr_custom_prob(self):
        gen = Bool(true_prob=0.8)
        assert "0.8" in repr(gen)
