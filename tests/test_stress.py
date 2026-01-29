"""
Tests for oigen.stress module.
"""

import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from oigen.errors import StressTestError
from oigen.generators import Int
from oigen.stress import (
    StressResult,
    StressTest,
    _normalize_output,
    _run_executable,
)
from oigen.workflow import Workflow


class TestStressResult:
    def test_str_format(self):
        result = StressResult(
            iterations=100,
            hacks_found=2,
            timeouts=1,
            errors=0,
            elapsed_time=5.0,
            hack_files=[Path("hack_1.in"), Path("hack_2.in")],
        )
        s = str(result)
        assert "100" in s  # iterations
        assert "2" in s    # hacks_found
        assert "1" in s    # timeouts
        assert "5.00" in s  # elapsed_time

    def test_str_format_zero_time(self):
        result = StressResult(
            iterations=0,
            hacks_found=0,
            timeouts=0,
            errors=0,
            elapsed_time=0.0,
            hack_files=[],
        )
        s = str(result)
        assert "0" in s


class TestNormalizeOutput:
    def test_strips_trailing_whitespace(self):
        assert _normalize_output("hello   \n") == "hello"

    def test_strips_each_line(self):
        assert _normalize_output("line1  \nline2  \n") == "line1\nline2"

    def test_empty_string(self):
        assert _normalize_output("") == ""

    def test_preserves_leading_spaces(self):
        assert _normalize_output("  hello\n") == "  hello"


class TestRunExecutable:
    def test_successful_run(self):
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "output"
        mock_result.stderr = ""

        with patch("subprocess.run", return_value=mock_result):
            stdout, code, err = _run_executable("/bin/test", "input", 5.0)

        assert stdout == "output"
        assert code == 0
        assert err is None

    def test_nonzero_exit_code(self):
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = "partial output"
        mock_result.stderr = "error message"

        with patch("subprocess.run", return_value=mock_result):
            stdout, code, err = _run_executable("/bin/test", "input", 5.0)

        assert stdout == "partial output"
        assert code == 1
        assert err == "error message"

    def test_nonzero_exit_no_stderr(self):
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = ""
        mock_result.stderr = ""

        with patch("subprocess.run", return_value=mock_result):
            stdout, code, err = _run_executable("/bin/test", "input", 5.0)

        assert code == 1
        assert err == "Non-zero exit code"

    def test_timeout(self):
        with patch("subprocess.run", side_effect=subprocess.TimeoutExpired("cmd", 5)):
            stdout, code, err = _run_executable("/bin/test", "input", 5.0)

        assert stdout is None
        assert code is None
        assert err == "timeout"

    def test_file_not_found(self):
        with patch("subprocess.run", side_effect=FileNotFoundError()):
            with pytest.raises(StressTestError) as exc_info:
                _run_executable("/nonexistent", "input", 5.0)

        assert "not found" in str(exc_info.value)

    def test_permission_error(self):
        with patch("subprocess.run", side_effect=PermissionError()):
            with pytest.raises(StressTestError) as exc_info:
                _run_executable("/no_permission", "input", 5.0)

        assert "Permission denied" in str(exc_info.value)


class TestStressTest:
    @pytest.fixture
    def mock_workflow(self):
        gen = Int(1, 100)
        return Workflow(gen)

    @pytest.fixture
    def temp_executables(self, tmp_path):
        std = tmp_path / "std"
        hack = tmp_path / "hack"
        std.write_text("#!/bin/bash\necho 'output'")
        hack.write_text("#!/bin/bash\necho 'output'")
        std.chmod(0o755)
        hack.chmod(0o755)
        return std, hack

    def test_init_validates_std_exists(self, mock_workflow, tmp_path):
        hack = tmp_path / "hack"
        hack.write_text("test")

        with pytest.raises(StressTestError) as exc_info:
            StressTest(mock_workflow, "/nonexistent", hack)

        assert "Standard executable not found" in str(exc_info.value)

    def test_init_validates_hack_exists(self, mock_workflow, tmp_path):
        std = tmp_path / "std"
        std.write_text("test")

        with pytest.raises(StressTestError) as exc_info:
            StressTest(mock_workflow, std, "/nonexistent")

        assert "Hack executable not found" in str(exc_info.value)

    def test_init_validates_positive_timeout(self, mock_workflow, temp_executables):
        std, hack = temp_executables

        with pytest.raises(StressTestError) as exc_info:
            StressTest(mock_workflow, std, hack, timeout=0)

        assert "Timeout must be positive" in str(exc_info.value)

    def test_init_validates_negative_timeout(self, mock_workflow, temp_executables):
        std, hack = temp_executables

        with pytest.raises(StressTestError) as exc_info:
            StressTest(mock_workflow, std, hack, timeout=-1)

        assert "Timeout must be positive" in str(exc_info.value)

    def test_run_requires_max_iterations_or_until_hack(self, mock_workflow, temp_executables):
        std, hack = temp_executables
        stress = StressTest(mock_workflow, std, hack)

        with pytest.raises(StressTestError) as exc_info:
            with patch("oigen.stress.console"):
                stress.run()

        assert "Must specify max_iterations or until_hack" in str(exc_info.value)

    def test_run_detects_output_mismatch(self, mock_workflow, temp_executables, tmp_path):
        std, hack = temp_executables
        output_dir = tmp_path / "output"
        stress = StressTest(mock_workflow, std, hack, output=output_dir)

        def mock_run_exec(exe, input_data, timeout):
            if "std" in str(exe):
                return "correct", 0, None
            else:
                return "wrong", 0, None

        with patch("oigen.stress._run_executable", side_effect=mock_run_exec):
            with patch("oigen.stress.console"):
                result = stress.run(max_iterations=1, seed=42)

        assert result.iterations == 1
        assert result.hacks_found == 1
        assert len(result.hack_files) == 1

    def test_run_handles_timeout(self, mock_workflow, temp_executables, tmp_path):
        std, hack = temp_executables
        output_dir = tmp_path / "output"
        stress = StressTest(mock_workflow, std, hack, output=output_dir)

        def mock_run_exec(exe, input_data, timeout):
            return None, None, "timeout"

        with patch("oigen.stress._run_executable", side_effect=mock_run_exec):
            with patch("oigen.stress.console"):
                result = stress.run(max_iterations=3, seed=42)

        assert result.iterations == 3
        assert result.timeouts == 3
        assert result.hacks_found == 0

    def test_run_handles_std_runtime_error(self, mock_workflow, temp_executables, tmp_path):
        std, hack = temp_executables
        output_dir = tmp_path / "output"
        stress = StressTest(mock_workflow, std, hack, output=output_dir)

        def mock_run_exec(exe, input_data, timeout):
            if "std" in str(exe):
                return "output", 1, "error"  # std returns error
            return "output", 0, None

        with patch("oigen.stress._run_executable", side_effect=mock_run_exec):
            with patch("oigen.stress.console"):
                result = stress.run(max_iterations=1, seed=42)

        assert result.errors == 1
        assert result.hacks_found == 1  # std error counts as hack

    def test_run_handles_hack_runtime_error(self, mock_workflow, temp_executables, tmp_path):
        std, hack = temp_executables
        output_dir = tmp_path / "output"
        stress = StressTest(mock_workflow, std, hack, output=output_dir)

        def mock_run_exec(exe, input_data, timeout):
            if "hack" in str(exe):
                return "output", 1, "error"  # hack returns error
            return "output", 0, None

        with patch("oigen.stress._run_executable", side_effect=mock_run_exec):
            with patch("oigen.stress.console"):
                result = stress.run(max_iterations=1, seed=42)

        assert result.hacks_found == 1

    def test_run_until_hack_stops_early(self, mock_workflow, temp_executables, tmp_path):
        std, hack = temp_executables
        output_dir = tmp_path / "output"
        stress = StressTest(mock_workflow, std, hack, output=output_dir)

        call_count = 0

        def mock_run_exec(exe, input_data, timeout):
            nonlocal call_count
            call_count += 1
            if "std" in str(exe):
                return "correct", 0, None
            else:
                return "wrong", 0, None  # Always different

        with patch("oigen.stress._run_executable", side_effect=mock_run_exec):
            with patch("oigen.stress.console"):
                result = stress.run(until_hack=True, seed=42)

        assert result.iterations == 1
        assert result.hacks_found == 1

    def test_run_no_hacks_found(self, mock_workflow, temp_executables, tmp_path):
        std, hack = temp_executables
        output_dir = tmp_path / "output"
        stress = StressTest(mock_workflow, std, hack, output=output_dir)

        def mock_run_exec(exe, input_data, timeout):
            return "same output", 0, None

        with patch("oigen.stress._run_executable", side_effect=mock_run_exec):
            with patch("oigen.stress.console"):
                result = stress.run(max_iterations=5, seed=42)

        assert result.iterations == 5
        assert result.hacks_found == 0
        assert len(result.hack_files) == 0

    def test_save_hack_creates_files(self, mock_workflow, temp_executables, tmp_path):
        std, hack = temp_executables
        output_dir = tmp_path / "output"
        stress = StressTest(mock_workflow, std, hack, output=output_dir)

        input_path = stress._save_hack(1, "input data", "std out", "hack out")

        assert input_path.exists()
        assert input_path.read_text() == "input data"
        assert (output_dir / "hack_1.std.out").exists()
        assert (output_dir / "hack_1.hack.out").exists()

    def test_save_hack_handles_none_outputs(self, mock_workflow, temp_executables, tmp_path):
        std, hack = temp_executables
        output_dir = tmp_path / "output"
        stress = StressTest(mock_workflow, std, hack, output=output_dir)

        input_path = stress._save_hack(1, "input data", None, None)

        assert input_path.exists()
        assert not (output_dir / "hack_1.std.out").exists()
        assert not (output_dir / "hack_1.hack.out").exists()
