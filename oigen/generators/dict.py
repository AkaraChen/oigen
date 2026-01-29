"""
Dict generator for structured key-value data.
"""

from random import Random
from typing import Any

from oigen.errors import ConstraintError
from oigen.generators import BaseGenerator


class Dict(BaseGenerator):
    """Generator for dictionaries with specified schema.

    Args:
        schema: Mapping of keys to generators.

    Raises:
        ConstraintError: If schema is empty or contains non-generators.

    Example:
        >>> gen = Dict({"name": Char(), "age": Int(1, 100)})
        >>> value = gen.generate(Random())  # {"name": "x", "age": 42}
    """

    def __init__(self, schema: dict[str, BaseGenerator]):
        self.schema = schema
        self.validate()

    def validate(self) -> None:
        if not self.schema:
            raise ConstraintError(
                "Dict: schema cannot be empty",
                suggestion="Provide at least one key-value pair in the schema",
            )

        for key, value in self.schema.items():
            if not isinstance(value, BaseGenerator):
                raise ConstraintError(
                    f"Dict: value for key '{key}' must be a generator, "
                    f"got {type(value).__name__}",
                    suggestion=f"Use a generator like Int() or Char() for '{key}'",
                )

    def generate(self, rng: Random) -> dict[str, Any]:
        return {key: gen.generate(rng) for key, gen in self.schema.items()}

    def __repr__(self) -> str:
        schema_repr = ", ".join(f"{k!r}: {v!r}" for k, v in self.schema.items())
        return f"Dict({{{schema_repr}}})"
