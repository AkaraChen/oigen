"""
Generator modules for oigen data generation.
"""

from abc import ABC, abstractmethod
from random import Random
from typing import Any


class BaseGenerator(ABC):
    """Abstract base class for all generators.

    All generators must inherit from this class and implement the generate method.
    Generators can be composed to create complex data structures.
    """

    @abstractmethod
    def generate(self, rng: Random) -> Any:
        """Generate a random value using the provided RNG.

        Args:
            rng: A Random instance for deterministic generation.

        Returns:
            The generated value. Type depends on the specific generator.
        """
        pass

    def validate(self) -> None:
        """Validate generator constraints.

        Override this method to add constraint validation.
        Called during generator construction.

        Raises:
            ConstraintError: If constraints are invalid.
        """
        pass

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}()"


# Import all generators for convenient access
from oigen.generators.primitives import Int, Double, Char, Bool
from oigen.generators.sequence import Sequence
from oigen.generators.tree import Tree
from oigen.generators.graph import Graph

__all__ = [
    "BaseGenerator",
    "Int",
    "Double",
    "Char",
    "Bool",
    "Sequence",
    "Tree",
    "Graph",
]
