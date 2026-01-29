"""
Tests for oigen.output module.
"""

from io import StringIO
from unittest.mock import patch, MagicMock

import pytest
from rich.console import Console as RichConsole
from rich.progress import Progress
from rich.table import Table

from oigen.output import (
    Verbosity,
    Console,
    console,
    error,
    success,
    warning,
    info,
    debug,
    set_verbosity,
)


class TestVerbosity:
    def test_enum_values(self):
        assert Verbosity.QUIET.value == 0
        assert Verbosity.DEFAULT.value == 1
        assert Verbosity.VERBOSE.value == 2

    def test_comparison(self):
        assert Verbosity.QUIET.value < Verbosity.DEFAULT.value
        assert Verbosity.DEFAULT.value < Verbosity.VERBOSE.value


class TestConsole:
    def test_default_verbosity(self):
        c = Console()
        assert c.verbosity == Verbosity.DEFAULT

    def test_custom_verbosity(self):
        c = Console(verbosity=Verbosity.QUIET)
        assert c.verbosity == Verbosity.QUIET

    def test_verbosity_setter(self):
        c = Console()
        c.verbosity = Verbosity.VERBOSE
        assert c.verbosity == Verbosity.VERBOSE

    def test_is_terminal_property(self):
        c = Console(force_terminal=True)
        assert c.is_terminal is True

        c = Console(force_terminal=False)
        assert c.is_terminal is False

    def test_error_always_prints(self):
        # Error should print even in quiet mode
        c = Console(verbosity=Verbosity.QUIET, force_terminal=False)
        with patch.object(c._console, 'print') as mock_print:
            c.error("test error")
            assert mock_print.called

    def test_error_with_suggestion(self):
        c = Console(force_terminal=False)
        with patch.object(c._console, 'print') as mock_print:
            c.error("test error", suggestion="try this")
            assert mock_print.call_count == 2

    def test_success_respects_quiet_mode(self):
        c = Console(verbosity=Verbosity.QUIET, force_terminal=False)
        with patch.object(c._console, 'print') as mock_print:
            c.success("done")
            assert not mock_print.called

    def test_success_prints_in_default_mode(self):
        c = Console(verbosity=Verbosity.DEFAULT, force_terminal=False)
        with patch.object(c._console, 'print') as mock_print:
            c.success("done")
            assert mock_print.called

    def test_warning_respects_quiet_mode(self):
        c = Console(verbosity=Verbosity.QUIET, force_terminal=False)
        with patch.object(c._console, 'print') as mock_print:
            c.warning("warn")
            assert not mock_print.called

    def test_warning_prints_in_default_mode(self):
        c = Console(verbosity=Verbosity.DEFAULT, force_terminal=False)
        with patch.object(c._console, 'print') as mock_print:
            c.warning("warn")
            assert mock_print.called

    def test_info_respects_quiet_mode(self):
        c = Console(verbosity=Verbosity.QUIET, force_terminal=False)
        with patch.object(c._console, 'print') as mock_print:
            c.info("info message")
            assert not mock_print.called

    def test_info_prints_in_default_mode(self):
        c = Console(verbosity=Verbosity.DEFAULT, force_terminal=False)
        with patch.object(c._console, 'print') as mock_print:
            c.info("info message")
            assert mock_print.called

    def test_debug_only_in_verbose_mode(self):
        c = Console(verbosity=Verbosity.DEFAULT, force_terminal=False)
        with patch.object(c._console, 'print') as mock_print:
            c.debug("debug message")
            assert not mock_print.called

        c = Console(verbosity=Verbosity.VERBOSE, force_terminal=False)
        with patch.object(c._console, 'print') as mock_print:
            c.debug("debug message")
            assert mock_print.called

    def test_print_respects_quiet_mode(self):
        c = Console(verbosity=Verbosity.QUIET, force_terminal=False)
        with patch.object(c._console, 'print') as mock_print:
            c.print("message")
            assert not mock_print.called

    def test_print_always_ignores_verbosity(self):
        c = Console(verbosity=Verbosity.QUIET, force_terminal=False)
        with patch.object(c._console, 'print') as mock_print:
            c.print_always("message")
            assert mock_print.called

    def test_progress_returns_progress_object(self):
        c = Console(force_terminal=False)
        progress = c.progress("Working...")
        assert isinstance(progress, Progress)

    def test_progress_with_total(self):
        c = Console(force_terminal=False)
        progress = c.progress("Working...", total=100)
        assert isinstance(progress, Progress)

    def test_progress_disabled_in_quiet_mode(self):
        c = Console(verbosity=Verbosity.QUIET, force_terminal=False)
        progress = c.progress("Working...")
        assert progress.disable is True

    def test_table_returns_table_object(self):
        c = Console()
        table = c.table()
        assert isinstance(table, Table)

    def test_table_with_title(self):
        c = Console()
        table = c.table(title="Test Table")
        assert table.title == "Test Table"

    def test_panel_respects_quiet_mode(self):
        c = Console(verbosity=Verbosity.QUIET, force_terminal=False)
        with patch.object(c._console, 'print') as mock_print:
            c.panel("content", title="Title")
            assert not mock_print.called

    def test_panel_prints_in_default_mode(self):
        c = Console(verbosity=Verbosity.DEFAULT, force_terminal=False)
        with patch.object(c._console, 'print') as mock_print:
            c.panel("content", title="Title")
            assert mock_print.called

    def test_render_table_respects_quiet_mode(self):
        c = Console(verbosity=Verbosity.QUIET, force_terminal=False)
        table = c.table()
        with patch.object(c._console, 'print') as mock_print:
            c.render_table(table)
            assert not mock_print.called

    def test_render_table_prints_in_default_mode(self):
        c = Console(verbosity=Verbosity.DEFAULT, force_terminal=False)
        table = c.table()
        with patch.object(c._console, 'print') as mock_print:
            c.render_table(table)
            assert mock_print.called


class TestModuleLevelFunctions:
    def test_error_uses_global_console(self):
        with patch.object(console, 'error') as mock_error:
            error("test", suggestion="hint")
            mock_error.assert_called_once_with("test", "hint")

    def test_success_uses_global_console(self):
        with patch.object(console, 'success') as mock_success:
            success("done")
            mock_success.assert_called_once_with("done")

    def test_warning_uses_global_console(self):
        with patch.object(console, 'warning') as mock_warning:
            warning("warn")
            mock_warning.assert_called_once_with("warn")

    def test_info_uses_global_console(self):
        with patch.object(console, 'info') as mock_info:
            info("info")
            mock_info.assert_called_once_with("info")

    def test_debug_uses_global_console(self):
        with patch.object(console, 'debug') as mock_debug:
            debug("debug")
            mock_debug.assert_called_once_with("debug")

    def test_set_verbosity(self):
        original = console.verbosity
        try:
            set_verbosity(Verbosity.VERBOSE)
            assert console.verbosity == Verbosity.VERBOSE
            set_verbosity(Verbosity.QUIET)
            assert console.verbosity == Verbosity.QUIET
        finally:
            console.verbosity = original
