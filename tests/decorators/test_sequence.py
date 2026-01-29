"""
Tests for oigen.decorators.sequence module.
"""

import pytest

from oigen.decorators.base import ConstraintRegistry, get_constraints
from oigen.decorators.sequence import (
    MonotonicConstraint,
    PrefixSumBoundedConstraint,
    RelationConstraint,
    monotonic,
    prefix_sum_bounded,
    with_relation,
)
from oigen.errors import ConstraintError
from oigen.generators import Int, Sequence


class TestRelationConstraint:
    def test_validate_valid(self):
        c = RelationConstraint(predicate=lambda a, b: a < b)
        c.validate(Sequence(Int(1, 10), length=5), ConstraintRegistry())

    def test_validate_not_callable(self):
        c = RelationConstraint(predicate="not callable")  # type: ignore
        with pytest.raises(ConstraintError) as exc_info:
            c.validate(Sequence(Int(1, 10), length=5), ConstraintRegistry())
        assert "callable" in str(exc_info.value)

    def test_apply(self):
        def pred(a, b):
            return a < b
        c = RelationConstraint(predicate=pred)
        context = {}
        c.apply(Sequence(Int(1, 10), length=5), context)
        assert context["relation_predicate"] is pred

    def test_priority(self):
        c = RelationConstraint(predicate=lambda a, b: True)
        assert c.priority == 20


class TestMonotonicConstraint:
    def test_validate_increasing(self):
        c = MonotonicConstraint(direction="increasing", strict=True)
        c.validate(Sequence(Int(1, 10), length=5), ConstraintRegistry())

    def test_validate_decreasing(self):
        c = MonotonicConstraint(direction="decreasing", strict=True)
        c.validate(Sequence(Int(1, 10), length=5), ConstraintRegistry())

    def test_validate_non_increasing(self):
        c = MonotonicConstraint(direction="non_increasing", strict=False)
        c.validate(Sequence(Int(1, 10), length=5), ConstraintRegistry())

    def test_validate_non_decreasing(self):
        c = MonotonicConstraint(direction="non_decreasing", strict=False)
        c.validate(Sequence(Int(1, 10), length=5), ConstraintRegistry())

    def test_validate_invalid_direction(self):
        c = MonotonicConstraint(direction="invalid", strict=True)
        with pytest.raises(ConstraintError) as exc_info:
            c.validate(Sequence(Int(1, 10), length=5), ConstraintRegistry())
        assert "direction" in str(exc_info.value)

    def test_apply(self):
        c = MonotonicConstraint(direction="increasing", strict=True)
        context = {}
        c.apply(Sequence(Int(1, 10), length=5), context)
        assert context["monotonic"] == "increasing"
        assert context["monotonic_strict"] is True

    def test_priority(self):
        c = MonotonicConstraint(direction="increasing", strict=True)
        assert c.priority == 15


class TestPrefixSumBoundedConstraint:
    def test_validate_valid(self):
        c = PrefixSumBoundedConstraint(max_val=100)
        c.validate(Sequence(Int(1, 10), length=5), ConstraintRegistry())

    def test_validate_warns_negative_elements(self):
        c = PrefixSumBoundedConstraint(max_val=100)
        # Should raise when element generator has negative min
        with pytest.raises(ConstraintError) as exc_info:
            c.validate(Sequence(Int(-10, 10), length=5), ConstraintRegistry())
        assert "negative" in str(exc_info.value)

    def test_apply(self):
        c = PrefixSumBoundedConstraint(max_val=100)
        context = {}
        c.apply(Sequence(Int(1, 10), length=5), context)
        assert context["prefix_sum_max"] == 100

    def test_priority(self):
        c = PrefixSumBoundedConstraint(max_val=100)
        assert c.priority == 20


class TestDecoratorFunctions:
    def test_with_relation(self):
        def pred(a, b):
            return abs(a - b) <= 5

        @with_relation(pred)
        def constrained():
            return Sequence(Int(1, 100), length=10)

        registry = get_constraints(constrained)
        assert registry is not None
        assert registry.has(RelationConstraint)

    def test_monotonic_default(self):
        @monotonic()
        def constrained():
            return Sequence(Int(1, 100), length=10)

        registry = get_constraints(constrained)
        assert registry is not None
        c = registry.get_one(MonotonicConstraint)
        assert c is not None
        assert c.direction == "increasing"
        assert c.strict is True

    def test_monotonic_decreasing(self):
        @monotonic("decreasing", strict=False)
        def constrained():
            return Sequence(Int(1, 100), length=10)

        registry = get_constraints(constrained)
        c = registry.get_one(MonotonicConstraint)
        assert c is not None
        assert c.direction == "decreasing"
        assert c.strict is False

    def test_prefix_sum_bounded(self):
        @prefix_sum_bounded(1000)
        def constrained():
            return Sequence(Int(1, 100), length=20)

        registry = get_constraints(constrained)
        assert registry is not None
        c = registry.get_one(PrefixSumBoundedConstraint)
        assert c is not None
        assert c.max_val == 1000
