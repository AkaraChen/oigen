"""
Tests for oigen.errors module.
"""

import pytest

from oigen.errors import (
    ConstraintError,
    GeneratorError,
    OigenError,
    StressTestError,
    WorkflowError,
)


class TestOigenError:
    def test_message_only(self):
        error = OigenError("Something went wrong")
        assert error.message == "Something went wrong"
        assert error.suggestion is None
        assert str(error) == "Something went wrong"

    def test_message_with_suggestion(self):
        error = OigenError("Something went wrong", suggestion="Try this fix")
        assert error.message == "Something went wrong"
        assert error.suggestion == "Try this fix"
        assert "Something went wrong" in str(error)
        assert "Try this fix" in str(error)

    def test_is_exception(self):
        error = OigenError("test")
        assert isinstance(error, Exception)

    def test_can_be_raised(self):
        with pytest.raises(OigenError) as exc_info:
            raise OigenError("test error", suggestion="test suggestion")
        assert exc_info.value.message == "test error"
        assert exc_info.value.suggestion == "test suggestion"


class TestConstraintError:
    def test_inheritance(self):
        error = ConstraintError("constraint violated")
        assert isinstance(error, OigenError)
        assert isinstance(error, Exception)

    def test_can_catch_as_oigen_error(self):
        with pytest.raises(OigenError):
            raise ConstraintError("test")


class TestGeneratorError:
    def test_inheritance(self):
        error = GeneratorError("generation failed")
        assert isinstance(error, OigenError)
        assert isinstance(error, Exception)

    def test_can_catch_as_oigen_error(self):
        with pytest.raises(OigenError):
            raise GeneratorError("test")


class TestWorkflowError:
    def test_inheritance(self):
        error = WorkflowError("workflow failed")
        assert isinstance(error, OigenError)
        assert isinstance(error, Exception)

    def test_can_catch_as_oigen_error(self):
        with pytest.raises(OigenError):
            raise WorkflowError("test")


class TestStressTestError:
    def test_inheritance(self):
        error = StressTestError("stress test failed")
        assert isinstance(error, OigenError)
        assert isinstance(error, Exception)

    def test_can_catch_as_oigen_error(self):
        with pytest.raises(OigenError):
            raise StressTestError("test")
