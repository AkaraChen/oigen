"""
Sequence generator for lists of elements.
"""

from random import Random
from typing import Any

from oigen.errors import ConstraintError
from oigen.generators import BaseGenerator


class Sequence(BaseGenerator):
    """Generator for sequences (lists) of elements.

    Args:
        element: Generator for each element in the sequence.
        length: Fixed length (int) or range (tuple of min, max).

    Raises:
        ConstraintError: If element is not a generator or length is invalid.

    Example:
        >>> gen = Sequence(Int(1, 10), length=5)  # List of 5 ints
        >>> gen = Sequence(Int(1, 10), length=(3, 7))  # List of 3-7 ints
    """

    def __init__(
        self,
        element: BaseGenerator,
        length: int | tuple[int, int] = 10,
    ):
        self.element = element
        self.length = length
        self.validate()

    def validate(self) -> None:
        if not isinstance(self.element, BaseGenerator):
            raise ConstraintError(
                f"Sequence: element must be a generator, got {type(self.element).__name__}",
                suggestion="Use a generator like Int(), Char(), or Dict() for the element",
            )

        if isinstance(self.length, tuple):
            min_len, max_len = self.length
            if min_len < 0:
                raise ConstraintError(
                    f"Sequence: minimum length ({min_len}) cannot be negative",
                    suggestion="Use a non-negative minimum length",
                )
            if min_len > max_len:
                raise ConstraintError(
                    f"Sequence: min length ({min_len}) must be <= max length ({max_len})",
                    suggestion="Swap the min and max length values",
                )
        elif isinstance(self.length, int):
            if self.length < 0:
                raise ConstraintError(
                    f"Sequence: length ({self.length}) cannot be negative",
                    suggestion="Use a non-negative length value",
                )
        else:
            raise ConstraintError(
                f"Sequence: length must be int or tuple, got {type(self.length).__name__}",
                suggestion="Use an integer for fixed length or tuple (min, max) for variable length",
            )

    def generate(self, rng: Random) -> list[Any]:
        if isinstance(self.length, tuple):
            min_len, max_len = self.length
            actual_length = rng.randint(min_len, max_len)
        else:
            actual_length = self.length

        return [self.element.generate(rng) for _ in range(actual_length)]

    def __repr__(self) -> str:
        return f"Sequence({self.element!r}, length={self.length!r})"
