# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

oigen is an OI/ACM competitive programming test data generation framework with stress testing support. It provides a declarative, decorator-based system for generating random test cases.

## Commands

```bash
make dev        # Install dev dependencies (pdm install -G dev)
make test       # Run tests (pdm run pytest)
make cov        # Run tests with coverage report
make lint       # Lint code (pdm run ruff check oigen tests)
make fmt        # Format code (pdm run ruff format oigen tests)
make build      # Build package
```

Run a single test:
```bash
pdm run pytest tests/path/to/test.py::test_function -v
```

## Architecture

### Core Components

- **generators/** - Data generation components
  - `primitives.py` - Int, Double, Char, Bool generators
  - `sequence.py`, `tree.py`, `graph.py`, `string.py`, `matrix.py` - Complex data structures
  - All inherit from `BaseGenerator` with `generate(rng: Random) -> Any`

- **decorators/** - Constraint decorators that modify generator behavior
  - `base.py` - `Constraint` base class, `ConstraintRegistry`, `add_constraint()` helper
  - Constraint-specific files: `tree.py`, `graph.py`, `sequence.py`, `string.py`, `matrix.py`
  - Decorators have priority (lower = applied earlier); stacking order matters

- **workflow.py** - `Workflow` class and `@workflow` decorator for batch generation and formatting

- **stress.py** - `StressTest` class for comparing solutions (std vs hack)

- **output.py** - Console output with rich formatting and verbosity control

- **errors.py** - Exception hierarchy: `OigenError` base with `ConstraintError`, `GeneratorError`, `WorkflowError`, `StressTestError`

### Key Patterns

1. **Deterministic RNG**: Pass `Random` instance to `generate()` for reproducibility
2. **Constraint System**: Decorators collect constraints via `ConstraintRegistry`; validated and applied during generation
3. **Decorator Stacking**: Bottom-up application (innermost decorator applied first)
4. **Data Classes**: `TreeData`, `GraphData`, `StringData`, `MatrixData` for structured output
5. **Error Suggestions**: All exceptions include helpful suggestions for users

### Usage Pattern

```python
@with_diameter(5, 8)           # Applied 2nd
@with_edge_weight(Int(1, 100)) # Applied 1st
@workflow()
def tree_gen():
    return Tree(n=10)

tree_gen.run(output="./tests", count=10)
```

## Testing

- 90% minimum coverage required
- Tests mirror source structure: `tests/generators/`, `tests/decorators/`
- `conftest.py` provides seeded RNG fixtures
