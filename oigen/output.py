"""
Terminal output utilities with rich formatting support.
"""

from enum import Enum
from typing import Any

from rich.console import Console as RichConsole
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.table import Table
from rich.panel import Panel


class Verbosity(Enum):
    """Verbosity levels for output control."""
    QUIET = 0    # Only errors and final results
    DEFAULT = 1  # Progress and summaries
    VERBOSE = 2  # Debug information


class Console:
    """Wrapper around rich Console with oigen-specific formatting."""

    def __init__(
        self,
        verbosity: Verbosity = Verbosity.DEFAULT,
        force_terminal: bool | None = None,
        no_color: bool = False,
    ):
        """Initialize the console.

        Args:
            verbosity: Output verbosity level.
            force_terminal: Force terminal mode (None for auto-detect).
            no_color: Disable colors even if terminal supports them.
        """
        self._verbosity = verbosity
        self._console = RichConsole(
            force_terminal=force_terminal,
            no_color=no_color,
            highlight=False,
        )

    @property
    def verbosity(self) -> Verbosity:
        """Get current verbosity level."""
        return self._verbosity

    @verbosity.setter
    def verbosity(self, value: Verbosity) -> None:
        """Set verbosity level."""
        self._verbosity = value

    @property
    def is_terminal(self) -> bool:
        """Check if output is going to a terminal."""
        return self._console.is_terminal

    def error(self, message: str, suggestion: str | None = None) -> None:
        """Print an error message in red with ❌ emoji.

        Args:
            message: The error message.
            suggestion: Optional suggestion for fixing the error.
        """
        self._console.print(f"❌ [bold red]{message}[/bold red]")
        if suggestion:
            self._console.print(f"   💡 [dim]{suggestion}[/dim]")

    def success(self, message: str) -> None:
        """Print a success message in green with ✅ emoji.

        Args:
            message: The success message.
        """
        if self._verbosity == Verbosity.QUIET:
            return
        self._console.print(f"✅ [bold green]{message}[/bold green]")

    def warning(self, message: str) -> None:
        """Print a warning message in yellow with ⚠️ emoji.

        Args:
            message: The warning message.
        """
        if self._verbosity == Verbosity.QUIET:
            return
        self._console.print(f"⚠️  [bold yellow]{message}[/bold yellow]")

    def info(self, message: str) -> None:
        """Print an info message with 💡 emoji.

        Args:
            message: The info message.
        """
        if self._verbosity == Verbosity.QUIET:
            return
        self._console.print(f"💡 {message}")

    def debug(self, message: str) -> None:
        """Print a debug message (only in verbose mode).

        Args:
            message: The debug message.
        """
        if self._verbosity != Verbosity.VERBOSE:
            return
        self._console.print(f"[dim]🔍 {message}[/dim]")

    def print(self, *args: Any, **kwargs: Any) -> None:
        """Print raw output (respects quiet mode for non-errors)."""
        if self._verbosity == Verbosity.QUIET:
            return
        self._console.print(*args, **kwargs)

    def print_always(self, *args: Any, **kwargs: Any) -> None:
        """Print output regardless of verbosity level."""
        self._console.print(*args, **kwargs)

    def progress(
        self,
        description: str = "Working...",
        total: int | None = None,
    ) -> Progress:
        """Create a progress bar context manager.

        Args:
            description: Description text for the progress bar.
            total: Total number of steps (None for indeterminate).

        Returns:
            A rich Progress context manager.
        """
        if total is None:
            return Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self._console,
                disable=self._verbosity == Verbosity.QUIET,
            )
        return Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=self._console,
            disable=self._verbosity == Verbosity.QUIET,
        )

    def table(self, title: str | None = None) -> Table:
        """Create a table for structured output.

        Args:
            title: Optional table title.

        Returns:
            A rich Table object.
        """
        return Table(title=title)

    def panel(self, content: str, title: str | None = None) -> None:
        """Print content in a panel.

        Args:
            content: Panel content.
            title: Optional panel title.
        """
        if self._verbosity == Verbosity.QUIET:
            return
        self._console.print(Panel(content, title=title))

    def render_table(self, table: Table) -> None:
        """Render a table to the console.

        Args:
            table: The table to render.
        """
        if self._verbosity == Verbosity.QUIET:
            return
        self._console.print(table)


# Global console instance with default settings
console = Console()


# Convenience functions using the global console
def error(message: str, suggestion: str | None = None) -> None:
    """Print an error message."""
    console.error(message, suggestion)


def success(message: str) -> None:
    """Print a success message."""
    console.success(message)


def warning(message: str) -> None:
    """Print a warning message."""
    console.warning(message)


def info(message: str) -> None:
    """Print an info message."""
    console.info(message)


def debug(message: str) -> None:
    """Print a debug message."""
    console.debug(message)


def set_verbosity(verbosity: Verbosity) -> None:
    """Set global console verbosity."""
    console.verbosity = verbosity
