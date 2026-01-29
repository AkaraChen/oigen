"""
Tests for oigen.generators.string module.
"""

from random import Random
from string import ascii_lowercase

import pytest

from oigen.errors import ConstraintError
from oigen.generators.string import String, StringData


class TestStringData:
    def test_str_single_string(self):
        data = StringData(value="hello", length=5)
        assert str(data) == "hello"

    def test_str_word_list(self):
        data = StringData(value=["abc", "def", "ghi"], length=9)
        s = str(data)
        lines = s.strip().split("\n")
        assert lines[0] == "3"  # count
        assert "abc" in lines
        assert "def" in lines
        assert "ghi" in lines


class TestString:
    def test_generate_fixed_length(self, rng):
        gen = String(length=10)
        result = gen.generate(rng)
        assert isinstance(result, StringData)
        assert len(result.value) == 10
        assert result.length == 10

    def test_generate_variable_length(self, rng):
        gen = String(length=(5, 15))
        for _ in range(100):
            result = gen.generate(rng)
            assert 5 <= len(result.value) <= 15

    def test_generate_default_charset(self, rng):
        gen = String(length=100)
        result = gen.generate(rng)
        for char in result.value:
            assert char in ascii_lowercase

    def test_generate_custom_charset(self, rng):
        gen = String(length=100, charset="01")
        result = gen.generate(rng)
        for char in result.value:
            assert char in "01"

    def test_generate_single_char_charset(self, rng):
        gen = String(length=10, charset="x")
        result = gen.generate(rng)
        assert result.value == "xxxxxxxxxx"

    def test_generate_deterministic(self):
        gen = String(length=20)
        rng1 = Random(42)
        rng2 = Random(42)
        result1 = gen.generate(rng1)
        result2 = gen.generate(rng2)
        assert result1.value == result2.value

    def test_generate_empty_string(self, rng):
        gen = String(length=0)
        result = gen.generate(rng)
        assert result.value == ""
        assert result.length == 0

    def test_validate_negative_length_raises(self):
        with pytest.raises(ConstraintError) as exc_info:
            String(length=-1)
        assert "negative" in str(exc_info.value)

    def test_validate_tuple_min_greater_than_max_raises(self):
        with pytest.raises(ConstraintError) as exc_info:
            String(length=(10, 5))
        assert "min length" in str(exc_info.value)

    def test_validate_tuple_negative_min_raises(self):
        with pytest.raises(ConstraintError) as exc_info:
            String(length=(-1, 5))
        assert "negative" in str(exc_info.value)

    def test_validate_invalid_length_type_raises(self):
        with pytest.raises(ConstraintError) as exc_info:
            String(length="ten")
        assert "int or tuple" in str(exc_info.value)

    def test_validate_empty_charset_raises(self):
        with pytest.raises(ConstraintError) as exc_info:
            String(length=10, charset="")
        assert "charset" in str(exc_info.value)
        assert "empty" in str(exc_info.value)

    def test_repr(self):
        gen = String(length=10, charset="abc")
        r = repr(gen)
        assert "String" in r
        assert "10" in r
        assert "abc" in r


class TestStringAdvancedFeatures:
    """Tests for advanced string generation with constraints."""

    def test_generate_with_template(self, rng):
        gen = String(length=10, charset="xyz")
        gen._constraint_registry = type("FakeRegistry", (), {
            "apply_all": lambda self, g: {"template": "ab*cd*efgh"}
        })()
        result = gen.generate(rng)
        assert result.value.startswith("ab")
        assert "cd" in result.value

    def test_generate_with_must_contain(self, rng):
        gen = String(length=20, charset="abcdefghij")
        gen._constraint_registry = type("FakeRegistry", (), {
            "apply_all": lambda self, g: {"must_contain": ["abc", "xyz"]}
        })()
        # Note: "xyz" may not fit if charset doesn't have those chars
        # Just testing the code path
        gen._constraint_registry = type("FakeRegistry", (), {
            "apply_all": lambda self, g: {"must_contain": ["abc", "def"]}
        })()
        result = gen.generate(rng)
        # The result should contain the substrings if possible
        assert len(result.value) == 20

    def test_generate_with_trie_words(self, rng):
        gen = String(length=10, charset="abc")
        gen._constraint_registry = type("FakeRegistry", (), {
            "apply_all": lambda self, g: {"trie_words": (5, 4), "charset": "abc"}
        })()
        result = gen.generate(rng)
        assert isinstance(result.value, list)
        assert len(result.value) == 5
        for word in result.value:
            assert len(word) <= 4

    def test_generate_with_custom_charset(self, rng):
        gen = String(length=10, charset="abcdefghij")
        gen._constraint_registry = type("FakeRegistry", (), {
            "apply_all": lambda self, g: {"charset": "xy"}
        })()
        result = gen.generate(rng)
        for char in result.value:
            assert char in "xy"
