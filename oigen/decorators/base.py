"""
Base classes for constraint decorators.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from functools import wraps
from typing import Any, Callable, TypeVar

from oigen.errors import ConstraintError
from oigen.generators import BaseGenerator


@dataclass
class Constraint(ABC):
    """Base class for all generator constraints.

    Constraints are collected by decorators and applied during generation.
    Each constraint type defines how it affects the generation process.
    """

    @abstractmethod
    def validate(self, generator: BaseGenerator, registry: "ConstraintRegistry") -> None:
        """Validate this constraint against the generator and other constraints.

        Args:
            generator: The generator being constrained.
            registry: Registry containing all constraints.

        Raises:
            ConstraintError: If constraint is invalid or conflicts with others.
        """
        pass

    @abstractmethod
    def apply(self, generator: BaseGenerator, context: dict[str, Any]) -> None:
        """Apply this constraint to the generation context.

        Args:
            generator: The generator being constrained.
            context: Mutable context dict for passing data to generator.
        """
        pass

    @property
    def priority(self) -> int:
        """Priority for constraint application order (lower = earlier)."""
        return 100


@dataclass
class ConstraintRegistry:
    """Registry that collects and manages constraints for a generator.

    Constraints are added via decorators and validated before generation.
    """

    constraints: list[Constraint] = field(default_factory=list)
    _validated: bool = False

    def add(self, constraint: Constraint) -> None:
        """Add a constraint to the registry."""
        self.constraints.append(constraint)
        self._validated = False

    def get(self, constraint_type: type) -> list[Constraint]:
        """Get all constraints of a specific type."""
        return [c for c in self.constraints if isinstance(c, constraint_type)]

    def has(self, constraint_type: type) -> bool:
        """Check if registry has a constraint of the given type."""
        return any(isinstance(c, constraint_type) for c in self.constraints)

    def get_one(self, constraint_type: type) -> Constraint | None:
        """Get the first constraint of a specific type, or None."""
        for c in self.constraints:
            if isinstance(c, constraint_type):
                return c
        return None

    def validate_all(self, generator: BaseGenerator) -> None:
        """Validate all constraints against the generator.

        Args:
            generator: The generator being constrained.

        Raises:
            ConstraintError: If any constraint is invalid.
        """
        # Sort by priority for validation order
        sorted_constraints = sorted(self.constraints, key=lambda c: c.priority)

        for constraint in sorted_constraints:
            constraint.validate(generator, self)

        self._validated = True

    def apply_all(self, generator: BaseGenerator) -> dict[str, Any]:
        """Apply all constraints and return generation context.

        Args:
            generator: The generator being constrained.

        Returns:
            Context dict with constraint data for generation.
        """
        if not self._validated:
            self.validate_all(generator)

        context: dict[str, Any] = {}

        # Sort by priority for application order
        sorted_constraints = sorted(self.constraints, key=lambda c: c.priority)

        for constraint in sorted_constraints:
            constraint.apply(generator, context)

        return context

    def __len__(self) -> int:
        return len(self.constraints)

    def __bool__(self) -> bool:
        return len(self.constraints) > 0


# Attribute name for storing constraint registry on decorated functions
CONSTRAINT_REGISTRY_ATTR = "_oigen_constraints"


F = TypeVar("F", bound=Callable[..., BaseGenerator])


def constrained(func: F) -> F:
    """Decorator that enables constraint collection on a generator function.

    This is automatically applied by constraint decorators, but can be used
    explicitly for clarity.

    Example:
        @constrained
        def my_tree():
            return Tree(n=10)
    """
    if hasattr(func, CONSTRAINT_REGISTRY_ATTR):
        return func

    registry = ConstraintRegistry()

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> BaseGenerator:
        generator = func(*args, **kwargs)
        if not isinstance(generator, BaseGenerator):
            raise ConstraintError(
                f"Constrained function must return a generator, got {type(generator).__name__}",
                suggestion="Return a generator like Tree(), Graph(), Sequence(), etc.",
            )
        # Attach registry to generator for use during generation
        generator._constraint_registry = registry
        return generator

    setattr(wrapper, CONSTRAINT_REGISTRY_ATTR, registry)
    return wrapper  # type: ignore


def get_constraints(func_or_generator: Callable | BaseGenerator) -> ConstraintRegistry | None:
    """Get the constraint registry from a decorated function or generator.

    Args:
        func_or_generator: A decorated function or generator instance.

    Returns:
        ConstraintRegistry if constraints exist, None otherwise.
    """
    # Check function attribute
    if hasattr(func_or_generator, CONSTRAINT_REGISTRY_ATTR):
        return getattr(func_or_generator, CONSTRAINT_REGISTRY_ATTR)
    # Check generator attribute (set during function call)
    if hasattr(func_or_generator, "_constraint_registry"):
        return getattr(func_or_generator, "_constraint_registry")
    return None


def add_constraint(constraint: Constraint) -> Callable[[F], F]:
    """Create a decorator that adds a constraint to a generator function.

    This is the base mechanism for all constraint decorators.

    Args:
        constraint: The constraint to add.

    Returns:
        Decorator function.
    """
    def decorator(func: F) -> F:
        # Ensure function has constraint support
        wrapped = constrained(func)
        registry = getattr(wrapped, CONSTRAINT_REGISTRY_ATTR)
        registry.add(constraint)
        return wrapped  # type: ignore

    return decorator
