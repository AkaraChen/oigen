"""
Tests for oigen.decorators.base module.
"""

from dataclasses import dataclass
from random import Random
from typing import Any

import pytest

from oigen.errors import ConstraintError
from oigen.generators import BaseGenerator, Int
from oigen.decorators.base import (
    Constraint,
    ConstraintRegistry,
    constrained,
    get_constraints,
    add_constraint,
    CONSTRAINT_REGISTRY_ATTR,
)


# Test constraint implementation
@dataclass
class MockConstraint(Constraint):
    name: str
    value: int = 0

    def validate(self, generator: BaseGenerator, registry: ConstraintRegistry) -> None:
        if self.value < 0:
            raise ConstraintError(f"MockConstraint: value cannot be negative")

    def apply(self, generator: BaseGenerator, context: dict[str, Any]) -> None:
        context[self.name] = self.value

    @property
    def priority(self) -> int:
        return self.value  # Use value as priority for testing


class TestConstraint:
    def test_abstract_methods(self):
        # Constraint is abstract, cannot instantiate directly
        with pytest.raises(TypeError):
            Constraint()

    def test_default_priority(self):
        constraint = MockConstraint(name="test")
        # Our mock uses value as priority, default is 0
        assert constraint.priority == 0


class TestConstraintRegistry:
    def test_add_constraint(self):
        registry = ConstraintRegistry()
        constraint = MockConstraint(name="test")
        registry.add(constraint)
        assert len(registry) == 1

    def test_add_multiple_constraints(self):
        registry = ConstraintRegistry()
        registry.add(MockConstraint(name="a"))
        registry.add(MockConstraint(name="b"))
        assert len(registry) == 2

    def test_get_by_type(self):
        registry = ConstraintRegistry()
        registry.add(MockConstraint(name="a"))
        registry.add(MockConstraint(name="b"))

        result = registry.get(MockConstraint)
        assert len(result) == 2

    def test_get_by_type_empty(self):
        registry = ConstraintRegistry()
        result = registry.get(MockConstraint)
        assert result == []

    def test_has_constraint_type(self):
        registry = ConstraintRegistry()
        assert not registry.has(MockConstraint)

        registry.add(MockConstraint(name="test"))
        assert registry.has(MockConstraint)

    def test_get_one(self):
        registry = ConstraintRegistry()
        c1 = MockConstraint(name="first")
        c2 = MockConstraint(name="second")
        registry.add(c1)
        registry.add(c2)

        result = registry.get_one(MockConstraint)
        assert result is c1

    def test_get_one_not_found(self):
        registry = ConstraintRegistry()
        result = registry.get_one(MockConstraint)
        assert result is None

    def test_validate_all(self):
        registry = ConstraintRegistry()
        registry.add(MockConstraint(name="a", value=1))
        registry.add(MockConstraint(name="b", value=2))

        gen = Int(1, 10)
        registry.validate_all(gen)  # Should not raise

        assert registry._validated is True

    def test_validate_all_raises_on_invalid(self):
        registry = ConstraintRegistry()
        registry.add(MockConstraint(name="a", value=-1))  # Invalid

        gen = Int(1, 10)
        with pytest.raises(ConstraintError):
            registry.validate_all(gen)

    def test_validate_all_respects_priority(self):
        # Create a constraint that records when it's validated
        validation_order = []

        @dataclass
        class OrderedConstraint(Constraint):
            order: int

            def validate(self, generator, registry):
                validation_order.append(self.order)

            def apply(self, generator, context):
                pass

            @property
            def priority(self):
                return self.order

        registry = ConstraintRegistry()
        registry.add(OrderedConstraint(order=30))
        registry.add(OrderedConstraint(order=10))
        registry.add(OrderedConstraint(order=20))

        registry.validate_all(Int(1, 10))
        assert validation_order == [10, 20, 30]

    def test_apply_all(self):
        registry = ConstraintRegistry()
        registry.add(MockConstraint(name="a", value=1))
        registry.add(MockConstraint(name="b", value=2))

        gen = Int(1, 10)
        context = registry.apply_all(gen)

        assert context["a"] == 1
        assert context["b"] == 2

    def test_apply_all_validates_first(self):
        registry = ConstraintRegistry()
        registry.add(MockConstraint(name="a", value=1))

        assert registry._validated is False

        gen = Int(1, 10)
        registry.apply_all(gen)

        assert registry._validated is True

    def test_apply_all_respects_priority(self):
        application_order = []

        @dataclass
        class OrderedConstraint(Constraint):
            order: int

            def validate(self, generator, registry):
                pass

            def apply(self, generator, context):
                application_order.append(self.order)

            @property
            def priority(self):
                return self.order

        registry = ConstraintRegistry()
        registry.add(OrderedConstraint(order=30))
        registry.add(OrderedConstraint(order=10))
        registry.add(OrderedConstraint(order=20))

        registry.apply_all(Int(1, 10))
        assert application_order == [10, 20, 30]

    def test_len(self):
        registry = ConstraintRegistry()
        assert len(registry) == 0
        registry.add(MockConstraint(name="a"))
        assert len(registry) == 1

    def test_bool_empty(self):
        registry = ConstraintRegistry()
        assert not registry

    def test_bool_non_empty(self):
        registry = ConstraintRegistry()
        registry.add(MockConstraint(name="a"))
        assert registry


class TestConstrained:
    def test_attaches_registry(self):
        @constrained
        def my_gen():
            return Int(1, 10)

        assert hasattr(my_gen, CONSTRAINT_REGISTRY_ATTR)
        registry = getattr(my_gen, CONSTRAINT_REGISTRY_ATTR)
        assert isinstance(registry, ConstraintRegistry)

    def test_returns_generator(self, rng):
        @constrained
        def my_gen():
            return Int(1, 10)

        result = my_gen()
        assert isinstance(result, BaseGenerator)

    def test_generator_has_registry(self):
        @constrained
        def my_gen():
            return Int(1, 10)

        result = my_gen()
        assert hasattr(result, "_constraint_registry")

    def test_idempotent(self):
        @constrained
        @constrained
        def my_gen():
            return Int(1, 10)

        # Should have single registry, not nested
        registry = getattr(my_gen, CONSTRAINT_REGISTRY_ATTR)
        assert isinstance(registry, ConstraintRegistry)

    def test_non_generator_raises(self):
        @constrained
        def bad_gen():
            return 42

        with pytest.raises(ConstraintError) as exc_info:
            bad_gen()
        assert "must return a generator" in str(exc_info.value)


class TestGetConstraints:
    def test_from_decorated_function(self):
        @constrained
        def my_gen():
            return Int(1, 10)

        registry = get_constraints(my_gen)
        assert isinstance(registry, ConstraintRegistry)

    def test_from_generator_instance(self):
        @constrained
        def my_gen():
            return Int(1, 10)

        gen = my_gen()
        registry = get_constraints(gen)
        assert isinstance(registry, ConstraintRegistry)

    def test_from_undecorated_returns_none(self):
        def plain_func():
            return Int(1, 10)

        assert get_constraints(plain_func) is None

    def test_from_plain_generator_returns_none(self):
        gen = Int(1, 10)
        assert get_constraints(gen) is None


class TestAddConstraint:
    def test_creates_decorator(self):
        constraint = MockConstraint(name="test", value=42)
        decorator = add_constraint(constraint)
        assert callable(decorator)

    def test_adds_constraint_to_registry(self):
        constraint = MockConstraint(name="test", value=42)

        @add_constraint(constraint)
        def my_gen():
            return Int(1, 10)

        registry = get_constraints(my_gen)
        assert registry is not None
        assert len(registry) == 1
        assert registry.get_one(MockConstraint) is constraint

    def test_multiple_constraints(self):
        c1 = MockConstraint(name="a", value=1)
        c2 = MockConstraint(name="b", value=2)

        @add_constraint(c2)
        @add_constraint(c1)
        def my_gen():
            return Int(1, 10)

        registry = get_constraints(my_gen)
        assert len(registry) == 2

    def test_enables_constrained_automatically(self):
        constraint = MockConstraint(name="test", value=42)

        @add_constraint(constraint)
        def my_gen():
            return Int(1, 10)

        # Should have registry even without explicit @constrained
        assert hasattr(my_gen, CONSTRAINT_REGISTRY_ATTR)

    def test_constraint_applied_to_generator(self, rng):
        constraint = MockConstraint(name="test", value=42)

        @add_constraint(constraint)
        def my_gen():
            return Int(1, 10)

        gen = my_gen()
        registry = get_constraints(gen)
        assert registry is not None

        context = registry.apply_all(gen)
        assert context["test"] == 42
