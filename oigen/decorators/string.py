"""
String constraint decorators.
"""

from dataclasses import dataclass
from typing import Any, Callable, TypeVar

from oigen.decorators.base import Constraint, ConstraintRegistry, add_constraint
from oigen.errors import ConstraintError
from oigen.generators import BaseGenerator


F = TypeVar("F", bound=Callable[..., BaseGenerator])


# ============================================================================
# String Constraints
# ============================================================================


@dataclass
class CharsetConstraint(Constraint):
    """Constraint for character set."""

    chars: str

    def validate(self, generator: BaseGenerator, registry: ConstraintRegistry) -> None:
        if not self.chars:
            raise ConstraintError(
                "from_charset: chars cannot be empty",
                suggestion="Provide at least one character",
            )

        # Check compatibility with must_contain
        must_contain = registry.get_one(MustContainConstraint)
        if must_contain is not None:
            for substr in must_contain.substrings:
                for c in substr:
                    if c not in self.chars:
                        raise ConstraintError(
                            f"from_charset: charset '{self.chars}' does not contain "
                            f"character '{c}' from required substring '{substr}'",
                            suggestion=f"Add '{c}' to charset or remove substring '{substr}'",
                        )

    def apply(self, generator: BaseGenerator, context: dict[str, Any]) -> None:
        context["charset"] = self.chars

    @property
    def priority(self) -> int:
        return 5  # Apply early


@dataclass
class TemplateConstraint(Constraint):
    """Constraint for template-based generation."""

    pattern: str

    def validate(self, generator: BaseGenerator, registry: ConstraintRegistry) -> None:
        if not self.pattern:
            raise ConstraintError(
                "from_template: pattern cannot be empty",
                suggestion="Provide a pattern like 'ab*cd*'",
            )

    def apply(self, generator: BaseGenerator, context: dict[str, Any]) -> None:
        context["template"] = self.pattern

    @property
    def priority(self) -> int:
        return 10


@dataclass
class MustContainConstraint(Constraint):
    """Constraint for required substrings."""

    substrings: list[str]

    def validate(self, generator: BaseGenerator, registry: ConstraintRegistry) -> None:
        if not self.substrings:
            raise ConstraintError(
                "must_contain: substrings cannot be empty",
                suggestion="Provide at least one substring",
            )

        for s in self.substrings:
            if not s:
                raise ConstraintError(
                    "must_contain: empty strings not allowed",
                    suggestion="Remove empty strings from the list",
                )

    def apply(self, generator: BaseGenerator, context: dict[str, Any]) -> None:
        context["must_contain"] = self.substrings

    @property
    def priority(self) -> int:
        return 20


@dataclass
class TrieWordsConstraint(Constraint):
    """Constraint for generating trie-suitable word sets."""

    count: int
    max_depth: int

    def validate(self, generator: BaseGenerator, registry: ConstraintRegistry) -> None:
        if self.count < 1:
            raise ConstraintError(
                f"as_trie_words: count ({self.count}) must be >= 1",
                suggestion="Use a positive word count",
            )
        if self.max_depth < 1:
            raise ConstraintError(
                f"as_trie_words: max_depth ({self.max_depth}) must be >= 1",
                suggestion="Use a positive max depth",
            )

    def apply(self, generator: BaseGenerator, context: dict[str, Any]) -> None:
        context["trie_words"] = (self.count, self.max_depth)

    @property
    def priority(self) -> int:
        return 10


# ============================================================================
# Decorator Functions
# ============================================================================


def from_charset(chars: str) -> Callable[[F], F]:
    """Specify the character set for string generation.

    Args:
        chars: String of characters to choose from.

    Example:
        @from_charset("abc")
        def simple_string():
            return String(length=10)
    """
    return add_constraint(CharsetConstraint(chars))


def from_template(pattern: str) -> Callable[[F], F]:
    """Generate strings matching a template pattern.

    Use * as wildcard for any character from the charset.
    Other characters are literals.

    Args:
        pattern: Template pattern like "ab*cd*ef".

    Example:
        @from_template("ab*cd*")
        @from_charset("xyz")
        def template_string():
            return String(length=10)  # e.g., "abxcdyxxxx"
    """
    return add_constraint(TemplateConstraint(pattern))


def must_contain(*substrings: str) -> Callable[[F], F]:
    """Require the string to contain specific substrings.

    Args:
        substrings: One or more substrings that must appear.

    Example:
        @must_contain("abc", "xyz")
        def containing_string():
            return String(length=20)  # Contains both "abc" and "xyz"
    """
    return add_constraint(MustContainConstraint(list(substrings)))


def as_trie_words(count: int, max_depth: int) -> Callable[[F], F]:
    """Generate a set of words suitable for trie construction.

    The words will share some prefixes to make an interesting trie structure.

    Args:
        count: Number of words to generate.
        max_depth: Maximum word length.

    Example:
        @as_trie_words(count=10, max_depth=5)
        @from_charset("abc")
        def trie_data():
            return String()  # Returns list of words
    """
    return add_constraint(TrieWordsConstraint(count, max_depth))
