## Context

This is a greenfield Python package targeting OI/ACM problem setters. The codebase starts empty. Users are competitive programmers who want to:
1. Quickly generate test data for problems they're setting
2. Stress test solutions by comparing outputs of two programs
3. Have clear feedback when something goes wrong

The design must embrace modern Python patterns (decorators, type hints, dataclasses) while remaining approachable to users who may not be professional software engineers.

## Goals / Non-Goals

**Goals:**
- Provide a decorator-based API for defining data generation workflows
- Support composable generator modules for sequences, trees, graphs, dicts
- Enable one-line stress testing setup with automatic failure collection
- Deliver clear, emoji-rich error messages in terminal
- Keep the public API surface minimal and intuitive

**Non-Goals:**
- GUI or web interface (CLI/library only)
- Integration with specific OJ platforms (Codeforces, Luogu, etc.)
- Problem statement generation or formatting
- ML-based data reinforcement (reserved for future extensibility)
- Support for Python < 3.10

## Decisions

### 1. Workflow Definition via Decorators

**Decision:** Use `@oigen.workflow` decorator to define data generation pipelines.

**Rationale:** Decorators provide a clean, declarative syntax that feels natural in modern Python. Users define "what data looks like" rather than "how to generate it step by step."

**Alternatives considered:**
- Class inheritance (too verbose, feels old-school)
- Builder pattern (requires chaining, less readable for complex structures)
- YAML/JSON config (loses Python's expressiveness, harder to debug)

### 2. Generator Composition Model

**Decision:** Generators are composable objects that can be nested. A `Sequence(Int(1, 100), length=10)` reads naturally as "a sequence of 10 integers from 1-100."

**Rationale:** Composition mirrors how OI data is structured (a tree of N nodes, each with value in range X). Natural mapping from problem constraints to code.

**Alternatives considered:**
- Separate functions per structure type (loses composition)
- String DSL (parsing overhead, poor IDE support)

### 3. Stress Testing Architecture

**Decision:** Stress tester takes a workflow, std path, and hack path. Runs in a loop: generate → execute both → compare → save failures.

**Rationale:** Simple mental model. Users already understand "generate data, run two programs, compare." We automate the loop.

**Alternatives considered:**
- Async parallel execution (added complexity, subprocess already parallelizes)
- Distributed testing (overkill for typical use case)

### 4. Terminal Output with Rich

**Decision:** Use `rich` library for colored output, progress bars, and formatted error messages.

**Rationale:** `rich` is well-maintained, has excellent API, and handles terminal compatibility. Avoids reinventing ANSI escape code handling.

**Alternatives considered:**
- `colorama` (lower-level, more manual work)
- `click` styling (only for CLI apps, not general output)
- Raw ANSI codes (portability issues on Windows)

### 5. Package Structure

**Decision:** Flat module structure under `oigen/`:
```
oigen/
  __init__.py      # Public API exports
  workflow.py      # Workflow decorator and runner
  generators/      # Built-in generator modules
    __init__.py
    primitives.py  # Int, Double, Char, Bool
    sequence.py    # Sequence
    tree.py        # Tree
    graph.py       # Graph
    dict.py        # Dict/Mapping
  stress.py        # Stress testing runner
  output.py        # Terminal output (rich wrapper)
  errors.py        # Custom exceptions with friendly messages
```

**Rationale:** Shallow hierarchy is easier to navigate. Generators get their own subpackage since they're numerous and cohesive.

### 6. Extensibility Hooks

**Decision:** Generators inherit from `BaseGenerator` with `generate(rng) -> Any` method. Users can create custom generators by subclassing.

**Rationale:** Explicit extension point for future ML integration (a "learned generator" could override `generate` to use a model). Also allows users to add domain-specific generators.

## Risks / Trade-offs

**[Risk]** Users may find decorator syntax unfamiliar → Provide clear examples in docs and error messages that suggest correct patterns

**[Risk]** `rich` dependency adds weight for a small utility → It's a single, well-maintained dependency; benefits outweigh ~500KB cost

**[Risk]** Graph generation for large N may be slow → Document performance characteristics; consider optional `networkx` integration later

**[Trade-off]** Python 3.10+ requirement excludes older environments → Modern syntax (match, type unions) significantly improves code quality; OI users typically have recent Python

**[Trade-off]** No async execution for stress testing → Simplicity wins; subprocess parallelism is sufficient for typical use
