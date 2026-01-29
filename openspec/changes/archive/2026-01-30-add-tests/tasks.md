## 1. Setup

- [x] 1.1 Create tests/ directory structure (tests/, tests/generators/, tests/decorators/)
- [x] 1.2 Create tests/conftest.py with seeded_random fixture
- [x] 1.3 Update pyproject.toml with coverage configuration (branch=true, fail_under=90)

## 2. Core Module Tests

- [x] 2.1 Create tests/test_errors.py (OigenError with/without suggestion, subclass inheritance)
- [x] 2.2 Create tests/test_output.py (Console verbosity levels, quiet/verbose mode, progress bar, mock rich.console)
- [x] 2.3 Create tests/test_workflow.py (generate_one, run with tmp_path, seed reproducibility, default_formatter for all types)
- [x] 2.4 Create tests/test_stress.py (mock subprocess, output mismatch detection, timeout handling, runtime error handling, early termination, validation)

## 3. Primitive Generator Tests

- [x] 3.1 Create tests/generators/test_primitives.py for Int (range validation, generate within bounds, min=max edge case)
- [x] 3.2 Add Double tests (precision, range validation)
- [x] 3.3 Add Char tests (charset validation, empty charset rejection)
- [x] 3.4 Add Bool tests (probability validation, probability distribution)

## 4. Complex Generator Tests

- [x] 4.1 Create tests/generators/test_sequence.py (fixed length, variable length, non-generator element rejection)
- [x] 4.2 Create tests/generators/test_tree.py (edge count, single node, node values, TreeData.__str__ formatting)
- [x] 4.3 Create tests/generators/test_graph.py (edge count, max edges for directed/undirected, self-loops, GraphData.__str__ formatting)
- [x] 4.4 Create tests/generators/test_string.py (fixed/variable length, charset, StringData.__str__ formatting)
- [x] 4.5 Create tests/generators/test_matrix.py (dimensions, variable dimensions, character/numeric formatting)

## 5. Decorator System Tests

- [x] 5.1 Create tests/decorators/test_base.py (constrained decorator, ConstraintRegistry add/get/has/get_one)
- [x] 5.2 Add tests for validate_all and apply_all methods
- [x] 5.3 Add tests for get_constraints and add_constraint utilities

## 6. Coverage Verification

- [x] 6.1 Run pytest --cov=oigen --cov-branch and identify uncovered branches
- [x] 6.2 Add additional test cases to reach 90% coverage
- [x] 6.3 Mark unreachable defensive code with # pragma: no cover if necessary
