"""
Custom exceptions for oigen with user-friendly error messages.
"""


class OigenError(Exception):
    """Base exception class for all oigen errors.

    Attributes:
        message: The error message describing what went wrong.
        suggestion: Optional suggestion for how to fix the error.
    """

    def __init__(self, message: str, suggestion: str | None = None):
        self.message = message
        self.suggestion = suggestion
        super().__init__(message)

    def __str__(self) -> str:
        if self.suggestion:
            return f"{self.message}\n💡 Suggestion: {self.suggestion}"
        return self.message


class ConstraintError(OigenError):
    """Raised when generator constraints are invalid."""
    pass


class GeneratorError(OigenError):
    """Raised when a generator fails during data generation."""
    pass


class WorkflowError(OigenError):
    """Raised when a workflow configuration or execution fails."""
    pass


class StressTestError(OigenError):
    """Raised when stress testing encounters an error."""
    pass
