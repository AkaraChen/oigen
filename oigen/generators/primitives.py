"""
Primitive generators: Int, Double, Char, Bool.
"""

from random import Random
from string import ascii_lowercase

from oigen.errors import ConstraintError
from oigen.generators import BaseGenerator


class Int(BaseGenerator):
    """Generator for random integers within a range.

    Args:
        min_val: Minimum value (inclusive).
        max_val: Maximum value (inclusive).

    Raises:
        ConstraintError: If min_val > max_val.

    Example:
        >>> gen = Int(1, 100)
        >>> value = gen.generate(Random())  # Random int from 1 to 100
    """

    def __init__(self, min_val: int = 0, max_val: int = 10**9):
        self.min_val = min_val
        self.max_val = max_val
        self.validate()

    def validate(self) -> None:
        if self.min_val > self.max_val:
            raise ConstraintError(
                f"Int: min ({self.min_val}) must be <= max ({self.max_val})",
                suggestion="Swap the min and max values",
            )

    def generate(self, rng: Random) -> int:
        return rng.randint(self.min_val, self.max_val)

    def __repr__(self) -> str:
        return f"Int({self.min_val}, {self.max_val})"


class Double(BaseGenerator):
    """Generator for random floating-point numbers within a range.

    Args:
        min_val: Minimum value (inclusive).
        max_val: Maximum value (inclusive).
        precision: Number of decimal places (default 6).

    Raises:
        ConstraintError: If min_val > max_val or precision < 0.

    Example:
        >>> gen = Double(0.0, 1.0, precision=2)
        >>> value = gen.generate(Random())  # e.g., 0.42
    """

    def __init__(
        self,
        min_val: float = 0.0,
        max_val: float = 1.0,
        precision: int = 6,
    ):
        self.min_val = min_val
        self.max_val = max_val
        self.precision = precision
        self.validate()

    def validate(self) -> None:
        if self.min_val > self.max_val:
            raise ConstraintError(
                f"Double: min ({self.min_val}) must be <= max ({self.max_val})",
                suggestion="Swap the min and max values",
            )
        if self.precision < 0:
            raise ConstraintError(
                f"Double: precision ({self.precision}) must be >= 0",
                suggestion="Use a non-negative precision value",
            )

    def generate(self, rng: Random) -> float:
        value = rng.uniform(self.min_val, self.max_val)
        return round(value, self.precision)

    def __repr__(self) -> str:
        return f"Double({self.min_val}, {self.max_val}, precision={self.precision})"


class Char(BaseGenerator):
    """Generator for random characters from a charset.

    Args:
        charset: String of characters to choose from (default: lowercase letters).

    Raises:
        ConstraintError: If charset is empty.

    Example:
        >>> gen = Char()  # Random lowercase letter
        >>> gen = Char("ABC123")  # Random from 'A', 'B', 'C', '1', '2', '3'
    """

    def __init__(self, charset: str = ascii_lowercase):
        self.charset = charset
        self.validate()

    def validate(self) -> None:
        if not self.charset:
            raise ConstraintError(
                "Char: charset cannot be empty",
                suggestion="Provide at least one character in the charset",
            )

    def generate(self, rng: Random) -> str:
        return rng.choice(self.charset)

    def __repr__(self) -> str:
        if self.charset == ascii_lowercase:
            return "Char()"
        return f"Char({self.charset!r})"


class Bool(BaseGenerator):
    """Generator for random boolean values.

    Args:
        true_prob: Probability of generating True (default 0.5).

    Raises:
        ConstraintError: If true_prob is not in [0, 1].

    Example:
        >>> gen = Bool()  # 50% chance of True
        >>> gen = Bool(true_prob=0.8)  # 80% chance of True
    """

    def __init__(self, true_prob: float = 0.5):
        self.true_prob = true_prob
        self.validate()

    def validate(self) -> None:
        if not 0 <= self.true_prob <= 1:
            raise ConstraintError(
                f"Bool: true_prob ({self.true_prob}) must be between 0 and 1",
                suggestion="Use a probability value between 0.0 and 1.0",
            )

    def generate(self, rng: Random) -> bool:
        return rng.random() < self.true_prob

    def __repr__(self) -> str:
        if self.true_prob == 0.5:
            return "Bool()"
        return f"Bool(true_prob={self.true_prob})"
