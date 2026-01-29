"""
Workflow system for data generation pipelines.
"""

from pathlib import Path
from random import Random
from typing import Any, Callable

from oigen.errors import WorkflowError
from oigen.generators import BaseGenerator
from oigen.output import console

# Type alias for formatter functions
Formatter = Callable[[Any], str]


def default_formatter(data: Any) -> str:
    """Default formatter that converts data to OI-style text output.

    Handles common data types:
    - Primitives: converted to string
    - Lists: space-separated on one line
    - Dicts: each key-value on separate line
    - TreeData/GraphData: uses their __str__ method
    """
    if hasattr(data, "__str__") and type(data).__str__ is not object.__str__:
        # Has custom __str__ (like TreeData, GraphData)
        return str(data)

    if isinstance(data, dict):
        lines = []
        for key, value in data.items():
            if isinstance(value, list):
                lines.append(" ".join(str(v) for v in value))
            else:
                lines.append(str(value))
        return "\n".join(lines)

    if isinstance(data, list):
        # Check if nested list
        if data and isinstance(data[0], list):
            return "\n".join(" ".join(str(v) for v in row) for row in data)
        return " ".join(str(v) for v in data)

    return str(data)


class Workflow:
    """Workflow for generating test data.

    A workflow wraps a generator and provides methods for batch generation
    with optional custom formatting.

    Args:
        generator: The root generator for this workflow.
        formatter: Optional custom formatter function.
        name: Optional workflow name for display.
    """

    def __init__(
        self,
        generator: BaseGenerator,
        formatter: Formatter | None = None,
        name: str | None = None,
    ):
        self.generator = generator
        self.formatter = formatter or default_formatter
        self.name = name

    def generate_one(self, rng: Random) -> Any:
        """Generate a single data instance.

        Args:
            rng: Random number generator for reproducibility.

        Returns:
            The generated data.
        """
        return self.generator.generate(rng)

    def format(self, data: Any) -> str:
        """Format generated data as text.

        Args:
            data: The generated data.

        Returns:
            Formatted string representation.
        """
        return self.formatter(data)

    def run(
        self,
        output: str | Path,
        count: int = 1,
        seed: int | None = None,
        filename_pattern: str = "{n}.in",
    ) -> list[Path]:
        """Generate multiple data files.

        Args:
            output: Directory to write files to.
            count: Number of files to generate.
            seed: Optional seed for reproducibility.
            filename_pattern: Pattern for filenames ({n} is replaced with index).

        Returns:
            List of paths to generated files.

        Raises:
            WorkflowError: If output directory cannot be created.
        """
        output_dir = Path(output)
        try:
            output_dir.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            raise WorkflowError(
                f"Cannot create output directory: {output_dir}",
                suggestion=f"Check permissions or path validity: {e}",
            )

        rng = Random(seed)
        generated_files: list[Path] = []

        workflow_name = self.name or "data"
        with console.progress(f"Generating {workflow_name}", total=count) as progress:
            task = progress.add_task(f"Generating {workflow_name}", total=count)

            for i in range(1, count + 1):
                data = self.generate_one(rng)
                formatted = self.format(data)

                filename = filename_pattern.format(n=i)
                filepath = output_dir / filename

                try:
                    filepath.write_text(formatted + "\n")
                except OSError as e:
                    raise WorkflowError(
                        f"Cannot write file: {filepath}",
                        suggestion=f"Check disk space and permissions: {e}",
                    )

                generated_files.append(filepath)
                progress.update(task, advance=1)

        console.success(f"Generated {count} file(s) in {output_dir}")
        return generated_files


def workflow(
    generator: BaseGenerator | None = None,
    formatter: Formatter | None = None,
    name: str | None = None,
) -> Workflow | Callable[[Callable[[], BaseGenerator]], Workflow]:
    """Decorator/factory for creating workflows.

    Can be used as a decorator or called directly:

    As decorator:
        @workflow
        def my_data():
            return Sequence(Int(1, 100), length=10)

    As decorator with options:
        @workflow(formatter=my_formatter, name="my_data")
        def my_data():
            return Sequence(Int(1, 100), length=10)

    Direct call:
        wf = workflow(Sequence(Int(1, 100), length=10))

    Args:
        generator: Root generator (for direct call).
        formatter: Optional custom formatter.
        name: Optional workflow name.

    Returns:
        Workflow instance or decorator function.
    """
    # Direct call with generator
    if generator is not None:
        if not isinstance(generator, BaseGenerator):
            raise WorkflowError(
                f"workflow() expects a generator, got {type(generator).__name__}",
                suggestion="Pass a generator like Sequence(), Tree(), or Graph()",
            )
        return Workflow(generator, formatter=formatter, name=name)

    # Used as decorator
    def decorator(func: Callable[[], BaseGenerator]) -> Workflow:
        gen = func()
        if not isinstance(gen, BaseGenerator):
            raise WorkflowError(
                f"Workflow function must return a generator, got {type(gen).__name__}",
                suggestion="Return a generator like Sequence(), Tree(), or Graph()",
            )
        return Workflow(gen, formatter=formatter, name=name or func.__name__)

    return decorator
