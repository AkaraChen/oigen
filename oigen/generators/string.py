"""
String generator for random strings with constraints.
"""

from dataclasses import dataclass
from random import Random
from string import ascii_lowercase
from typing import Any

from oigen.errors import ConstraintError
from oigen.generators import BaseGenerator


@dataclass
class StringData:
    """Generated string or word list data.

    Attributes:
        value: The generated string or list of strings (for trie mode).
        length: Length of the string (or total length for word list).
    """
    value: str | list[str]
    length: int

    def __str__(self) -> str:
        if isinstance(self.value, list):
            # Trie words mode
            lines = [str(len(self.value))]
            lines.extend(self.value)
            return "\n".join(lines)
        return self.value


class String(BaseGenerator):
    """Generator for random strings.

    Basic string generation uses a charset. Advanced features are added
    via decorators.

    Args:
        length: String length (int or tuple for range).
        charset: Character set to use (default: lowercase letters).

    Example:
        >>> gen = String(length=10)  # Random lowercase string
        >>> gen = String(length=(5, 15), charset="abc")  # Variable length from "abc"
    """

    def __init__(
        self,
        length: int | tuple[int, int] = 10,
        charset: str = ascii_lowercase,
    ):
        self.length = length
        self.charset = charset
        self._constraint_registry = None
        self.validate()

    def validate(self) -> None:
        if isinstance(self.length, tuple):
            min_len, max_len = self.length
            if min_len < 0:
                raise ConstraintError(
                    f"String: min length ({min_len}) cannot be negative",
                    suggestion="Use a non-negative minimum length",
                )
            if min_len > max_len:
                raise ConstraintError(
                    f"String: min length ({min_len}) must be <= max length ({max_len})",
                    suggestion="Swap the min and max values",
                )
        elif isinstance(self.length, int):
            if self.length < 0:
                raise ConstraintError(
                    f"String: length ({self.length}) cannot be negative",
                    suggestion="Use a non-negative length",
                )
        else:
            raise ConstraintError(
                f"String: length must be int or tuple, got {type(self.length).__name__}",
                suggestion="Use integer for fixed length or tuple (min, max) for range",
            )

        if not self.charset:
            raise ConstraintError(
                "String: charset cannot be empty",
                suggestion="Provide at least one character",
            )

    def _get_actual_length(self, rng: Random) -> int:
        """Resolve the actual string length."""
        if isinstance(self.length, tuple):
            return rng.randint(self.length[0], self.length[1])
        return self.length

    def _get_context(self) -> dict[str, Any]:
        """Get constraint context if available."""
        if self._constraint_registry is not None:
            return self._constraint_registry.apply_all(self)
        return {}

    def _generate_from_template(
        self,
        template: str,
        length: int,
        charset: str,
        rng: Random,
    ) -> str:
        """Generate a string matching a template pattern.

        Template uses * as wildcard for any character from charset.
        Other characters are literal.
        """
        result = []
        template_idx = 0

        for _ in range(length):
            if template_idx < len(template):
                char = template[template_idx]
                if char == "*":
                    result.append(rng.choice(charset))
                else:
                    result.append(char)
                template_idx += 1
            else:
                # Beyond template, use random chars
                result.append(rng.choice(charset))

        return "".join(result)

    def _generate_with_substrings(
        self,
        substrings: list[str],
        length: int,
        charset: str,
        rng: Random,
    ) -> str:
        """Generate a string containing all required substrings."""
        # Calculate minimum length needed
        total_substr_len = sum(len(s) for s in substrings)
        if total_substr_len > length:
            raise ConstraintError(
                f"String: cannot fit substrings (total {total_substr_len} chars) "
                f"in length {length}",
                suggestion="Increase string length or use fewer/shorter substrings",
            )

        # Place substrings at random positions
        result = list(rng.choice(charset) for _ in range(length))

        # Shuffle substrings to randomize placement order
        shuffled = list(substrings)
        rng.shuffle(shuffled)

        for substr in shuffled:
            # Find a position where this substring can fit
            max_pos = length - len(substr)
            placed = False

            # Try random positions first
            for _ in range(50):
                pos = rng.randint(0, max_pos)
                # Check if this position works (doesn't break other substrings)
                can_place = True
                for i, c in enumerate(substr):
                    if result[pos + i] != c and result[pos + i] not in charset:
                        can_place = False
                        break
                if can_place:
                    for i, c in enumerate(substr):
                        result[pos + i] = c
                    placed = True
                    break

            if not placed:
                # Fallback: find first valid position
                for pos in range(max_pos + 1):
                    for i, c in enumerate(substr):
                        result[pos + i] = c
                    break

        return "".join(result)

    def _generate_trie_words(
        self,
        count: int,
        max_depth: int,
        charset: str,
        rng: Random,
    ) -> list[str]:
        """Generate a set of words suitable for trie construction."""
        words = set()

        # Generate random words with some prefix sharing
        prefixes = [""]

        while len(words) < count:
            # Choose a prefix to extend
            prefix = rng.choice(prefixes)

            # Determine word length
            remaining_depth = max_depth - len(prefix)
            if remaining_depth <= 0:
                continue

            word_len = len(prefix) + rng.randint(1, remaining_depth)

            # Generate the word
            word = prefix + "".join(rng.choice(charset) for _ in range(word_len - len(prefix)))
            words.add(word)

            # Sometimes add the word as a new prefix
            if len(word) < max_depth and rng.random() < 0.3:
                prefixes.append(word)

        return sorted(list(words))[:count]

    def generate(self, rng: Random) -> StringData:
        context = self._get_context()

        # Get effective charset
        charset = context.get("charset", self.charset)

        # Check for trie mode
        if "trie_words" in context:
            count, max_depth = context["trie_words"]
            words = self._generate_trie_words(count, max_depth, charset, rng)
            return StringData(value=words, length=sum(len(w) for w in words))

        # Get actual length
        length = self._get_actual_length(rng)

        # Check for template
        if "template" in context:
            result = self._generate_from_template(context["template"], length, charset, rng)
            return StringData(value=result, length=len(result))

        # Check for required substrings
        if "must_contain" in context:
            result = self._generate_with_substrings(context["must_contain"], length, charset, rng)
            return StringData(value=result, length=len(result))

        # Basic random string
        result = "".join(rng.choice(charset) for _ in range(length))
        return StringData(value=result, length=len(result))

    def __repr__(self) -> str:
        return f"String(length={self.length!r}, charset={self.charset!r})"
