"""
Tests for oigen.decorators.string module.
"""

import pytest

from oigen.decorators.base import ConstraintRegistry, get_constraints
from oigen.decorators.string import (
    CharsetConstraint,
    MustContainConstraint,
    TemplateConstraint,
    TrieWordsConstraint,
    as_trie_words,
    from_charset,
    from_template,
    must_contain,
)
from oigen.errors import ConstraintError
from oigen.generators.string import String


class TestCharsetConstraint:
    def test_validate_valid(self):
        c = CharsetConstraint(chars="abc")
        c.validate(String(length=10), ConstraintRegistry())

    def test_validate_empty_chars(self):
        c = CharsetConstraint(chars="")
        with pytest.raises(ConstraintError) as exc_info:
            c.validate(String(length=10), ConstraintRegistry())
        assert "empty" in str(exc_info.value)

    def test_validate_incompatible_must_contain(self):
        c = CharsetConstraint(chars="abc")
        registry = ConstraintRegistry()
        registry.add(MustContainConstraint(substrings=["xyz"]))  # 'x' not in "abc"
        with pytest.raises(ConstraintError) as exc_info:
            c.validate(String(length=10), registry)
        assert "charset" in str(exc_info.value)

    def test_apply(self):
        c = CharsetConstraint(chars="abc")
        context = {}
        c.apply(String(length=10), context)
        assert context["charset"] == "abc"

    def test_priority(self):
        c = CharsetConstraint(chars="abc")
        assert c.priority == 5


class TestTemplateConstraint:
    def test_validate_valid(self):
        c = TemplateConstraint(pattern="ab*cd*")
        c.validate(String(length=10), ConstraintRegistry())

    def test_validate_empty_pattern(self):
        c = TemplateConstraint(pattern="")
        with pytest.raises(ConstraintError) as exc_info:
            c.validate(String(length=10), ConstraintRegistry())
        assert "empty" in str(exc_info.value)

    def test_apply(self):
        c = TemplateConstraint(pattern="ab*cd*")
        context = {}
        c.apply(String(length=10), context)
        assert context["template"] == "ab*cd*"

    def test_priority(self):
        c = TemplateConstraint(pattern="ab*")
        assert c.priority == 10


class TestMustContainConstraint:
    def test_validate_valid(self):
        c = MustContainConstraint(substrings=["abc", "xyz"])
        c.validate(String(length=20), ConstraintRegistry())

    def test_validate_empty_list(self):
        c = MustContainConstraint(substrings=[])
        with pytest.raises(ConstraintError) as exc_info:
            c.validate(String(length=20), ConstraintRegistry())
        assert "empty" in str(exc_info.value)

    def test_validate_empty_substring(self):
        c = MustContainConstraint(substrings=["abc", ""])
        with pytest.raises(ConstraintError) as exc_info:
            c.validate(String(length=20), ConstraintRegistry())
        assert "empty strings" in str(exc_info.value)

    def test_apply(self):
        c = MustContainConstraint(substrings=["abc", "xyz"])
        context = {}
        c.apply(String(length=20), context)
        assert context["must_contain"] == ["abc", "xyz"]

    def test_priority(self):
        c = MustContainConstraint(substrings=["abc"])
        assert c.priority == 20


class TestTrieWordsConstraint:
    def test_validate_valid(self):
        c = TrieWordsConstraint(count=10, max_depth=5)
        c.validate(String(length=10), ConstraintRegistry())

    def test_validate_count_less_than_1(self):
        c = TrieWordsConstraint(count=0, max_depth=5)
        with pytest.raises(ConstraintError) as exc_info:
            c.validate(String(length=10), ConstraintRegistry())
        assert "count" in str(exc_info.value)

    def test_validate_max_depth_less_than_1(self):
        c = TrieWordsConstraint(count=10, max_depth=0)
        with pytest.raises(ConstraintError) as exc_info:
            c.validate(String(length=10), ConstraintRegistry())
        assert "max_depth" in str(exc_info.value)

    def test_apply(self):
        c = TrieWordsConstraint(count=10, max_depth=5)
        context = {}
        c.apply(String(length=10), context)
        assert context["trie_words"] == (10, 5)

    def test_priority(self):
        c = TrieWordsConstraint(count=10, max_depth=5)
        assert c.priority == 10


class TestDecoratorFunctions:
    def test_from_charset(self):
        @from_charset("abc")
        def constrained():
            return String(length=10)

        registry = get_constraints(constrained)
        assert registry is not None
        assert registry.has(CharsetConstraint)

    def test_from_template(self):
        @from_template("ab*cd*")
        def constrained():
            return String(length=10)

        registry = get_constraints(constrained)
        assert registry is not None
        assert registry.has(TemplateConstraint)

    def test_must_contain(self):
        @must_contain("abc", "xyz")
        def constrained():
            return String(length=20)

        registry = get_constraints(constrained)
        assert registry is not None
        c = registry.get_one(MustContainConstraint)
        assert c is not None
        assert c.substrings == ["abc", "xyz"]

    def test_as_trie_words(self):
        @as_trie_words(count=10, max_depth=5)
        def constrained():
            return String(length=10)

        registry = get_constraints(constrained)
        assert registry is not None
        c = registry.get_one(TrieWordsConstraint)
        assert c is not None
        assert c.count == 10
        assert c.max_depth == 5
