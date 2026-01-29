"""
Stress testing system for comparing two executables.
"""

import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from random import Random
from typing import Any

from oigen.errors import StressTestError
from oigen.output import console
from oigen.workflow import Workflow


@dataclass
class StressResult:
    """Result of a stress test run.

    Attributes:
        iterations: Total iterations completed.
        hacks_found: Number of hacks (differing outputs) found.
        timeouts: Number of timeout occurrences.
        errors: Number of runtime errors.
        elapsed_time: Total time taken in seconds.
        hack_files: List of paths to saved hack input files.
    """
    iterations: int
    hacks_found: int
    timeouts: int
    errors: int
    elapsed_time: float
    hack_files: list[Path]

    def __str__(self) -> str:
        rate = self.iterations / self.elapsed_time if self.elapsed_time > 0 else 0
        return (
            f"Stress Test Complete\n"
            f"  Iterations: {self.iterations}\n"
            f"  Hacks found: {self.hacks_found}\n"
            f"  Timeouts: {self.timeouts}\n"
            f"  Errors: {self.errors}\n"
            f"  Time: {self.elapsed_time:.2f}s ({rate:.1f} iter/s)"
        )


def _normalize_output(output: str) -> str:
    """Normalize output for comparison (strip trailing whitespace per line)."""
    lines = output.rstrip().split("\n")
    return "\n".join(line.rstrip() for line in lines)


def _run_executable(
    executable: str | Path,
    input_data: str,
    timeout: float,
) -> tuple[str | None, int | None, str | None]:
    """Run an executable with input and return (output, exit_code, error).

    Returns:
        Tuple of (stdout, exit_code, error_message).
        If timeout, returns (None, None, "timeout").
        If error, returns (stdout_if_any, exit_code, stderr).
    """
    try:
        result = subprocess.run(
            [str(executable)],
            input=input_data,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        if result.returncode != 0:
            return result.stdout, result.returncode, result.stderr or "Non-zero exit code"
        return result.stdout, 0, None
    except subprocess.TimeoutExpired:
        return None, None, "timeout"
    except FileNotFoundError:
        raise StressTestError(
            f"Executable not found: {executable}",
            suggestion="Check the path and ensure the file exists and is executable",
        )
    except PermissionError:
        raise StressTestError(
            f"Permission denied: {executable}",
            suggestion="Check file permissions or run chmod +x on the executable",
        )


class StressTest:
    """Stress tester for comparing two executables.

    Generates random test data, runs both executables, and compares outputs.
    Saves failing cases (hacks) to the output directory.

    Args:
        workflow: Workflow for generating test data.
        std: Path to the "standard" (correct) executable.
        hack: Path to the "hack" (potentially incorrect) executable.
        output: Directory to save failing cases.
        timeout: Timeout for each executable run in seconds.

    Example:
        >>> stress = StressTest(my_workflow, "./std", "./hack", "./failures")
        >>> result = stress.run(max_iterations=1000)
    """

    def __init__(
        self,
        workflow: Workflow,
        std: str | Path,
        hack: str | Path,
        output: str | Path = "./stress_output",
        timeout: float = 5.0,
    ):
        self.workflow = workflow
        self.std = Path(std)
        self.hack = Path(hack)
        self.output = Path(output)
        self.timeout = timeout

        self._validate()

    def _validate(self) -> None:
        """Validate configuration."""
        if not self.std.exists():
            raise StressTestError(
                f"Standard executable not found: {self.std}",
                suggestion="Check the path or build the executable first",
            )
        if not self.hack.exists():
            raise StressTestError(
                f"Hack executable not found: {self.hack}",
                suggestion="Check the path or build the executable first",
            )
        if self.timeout <= 0:
            raise StressTestError(
                f"Timeout must be positive, got {self.timeout}",
                suggestion="Use a positive timeout value (e.g., 5.0 seconds)",
            )

    def _save_hack(
        self,
        hack_num: int,
        input_data: str,
        std_output: str | None,
        hack_output: str | None,
    ) -> Path:
        """Save a hack case to the output directory."""
        self.output.mkdir(parents=True, exist_ok=True)

        # Save input
        input_path = self.output / f"hack_{hack_num}.in"
        input_path.write_text(input_data)

        # Save outputs
        if std_output is not None:
            std_path = self.output / f"hack_{hack_num}.std.out"
            std_path.write_text(std_output)

        if hack_output is not None:
            hack_path = self.output / f"hack_{hack_num}.hack.out"
            hack_path.write_text(hack_output)

        return input_path

    def run(
        self,
        max_iterations: int | None = None,
        until_hack: bool = False,
        seed: int | None = None,
    ) -> StressResult:
        """Run stress test.

        Args:
            max_iterations: Maximum iterations (None for unlimited with until_hack).
            until_hack: If True, run until a hack is found.
            seed: Random seed for reproducibility.

        Returns:
            StressResult with test statistics.

        Raises:
            StressTestError: If configuration is invalid.
        """
        if max_iterations is None and not until_hack:
            raise StressTestError(
                "Must specify max_iterations or until_hack=True",
                suggestion="Use run(max_iterations=1000) or run(until_hack=True)",
            )

        rng = Random(seed)
        iterations = 0
        hacks_found = 0
        timeouts = 0
        errors = 0
        hack_files: list[Path] = []

        start_time = time.time()

        console.info(f"Starting stress test: {self.std} vs {self.hack}")
        console.info(f"Timeout: {self.timeout}s per run")

        try:
            while True:
                # Check termination conditions
                if max_iterations is not None and iterations >= max_iterations:
                    break
                if until_hack and hacks_found > 0:
                    break

                iterations += 1

                # Generate test data
                data = self.workflow.generate_one(rng)
                input_data = self.workflow.format(data)

                # Run both executables
                std_out, std_code, std_err = _run_executable(
                    self.std, input_data, self.timeout
                )
                hack_out, hack_code, hack_err = _run_executable(
                    self.hack, input_data, self.timeout
                )

                # Check for timeouts
                if std_err == "timeout" or hack_err == "timeout":
                    timeouts += 1
                    console.warning(f"Iteration {iterations}: Timeout")
                    continue

                # Check for runtime errors
                if std_code != 0:
                    errors += 1
                    hack_path = self._save_hack(
                        hacks_found + 1, input_data, std_out, hack_out
                    )
                    hack_files.append(hack_path)
                    hacks_found += 1
                    console.warning(
                        f"Iteration {iterations}: std runtime error (exit {std_code})"
                    )
                    continue

                if hack_code != 0:
                    # Hack runtime error counts as a hack
                    hack_path = self._save_hack(
                        hacks_found + 1, input_data, std_out, hack_out
                    )
                    hack_files.append(hack_path)
                    hacks_found += 1
                    console.success(
                        f"Hack #{hacks_found} found at iteration {iterations}: "
                        f"hack runtime error (exit {hack_code})"
                    )
                    continue

                # Compare outputs
                std_normalized = _normalize_output(std_out or "")
                hack_normalized = _normalize_output(hack_out or "")

                if std_normalized != hack_normalized:
                    hack_path = self._save_hack(
                        hacks_found + 1, input_data, std_out, hack_out
                    )
                    hack_files.append(hack_path)
                    hacks_found += 1
                    console.success(
                        f"Hack #{hacks_found} found at iteration {iterations}: "
                        f"output mismatch"
                    )

                # Progress update every 100 iterations
                if iterations % 100 == 0:
                    elapsed = time.time() - start_time
                    rate = iterations / elapsed if elapsed > 0 else 0
                    console.debug(
                        f"Progress: {iterations} iterations, "
                        f"{hacks_found} hacks, {rate:.1f} iter/s"
                    )

        except KeyboardInterrupt:
            console.warning("Stress test interrupted by user")

        elapsed_time = time.time() - start_time

        result = StressResult(
            iterations=iterations,
            hacks_found=hacks_found,
            timeouts=timeouts,
            errors=errors,
            elapsed_time=elapsed_time,
            hack_files=hack_files,
        )

        # Print summary
        console.print_always("")
        if hacks_found > 0:
            console.success(f"Found {hacks_found} hack(s)!")
            console.info(f"Saved to: {self.output}")
        else:
            console.success("No hacks found")

        console.print_always(str(result))

        return result
