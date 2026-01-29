## Why

OI/ACM problem setters currently write ad-hoc data generation scripts for each problem, leading to repetitive code, inconsistent data quality, and manual stress testing. A modern Python framework can standardize data generation workflows and automate hack discovery, significantly reducing effort while improving data coverage.

## What Changes

- Introduce a declarative workflow-based data generation system using decorators and modular composition
- Support generating common OI/ACM data structures: sequences, trees, graphs, and dictionaries
- Support base element types: int, double, char, bool with configurable constraints
- Add stress testing capability to automatically compare two executables and collect failing cases
- Provide rich terminal output with colors and emoji for friendly error messages
- Design extensible architecture for future ML-based data reinforcement

## Capabilities

### New Capabilities

- `data-generation`: Core workflow engine for composing data generators using decorators and modules. Supports sequences, trees, graphs, dicts with int/double/char/bool elements. Configurable constraints (size, value range, structural validity).
- `stress-testing`: Automated comparison of std vs hack executables. Generates random data, runs both programs, saves cases where outputs differ.
- `terminal-output`: Rich terminal output system with colored text, emoji indicators, and user-friendly error messages with suggestions.

### Modified Capabilities

(None - this is a new project)

## Impact

- **New package**: `oigen` Python package with pip-installable distribution
- **Dependencies**: `rich` or similar for terminal output, standard library for subprocess execution
- **API surface**: Decorator-based workflow definition, generator modules, stress test runner
- **Target Python**: 3.10+ (modern type hints, match statements)
