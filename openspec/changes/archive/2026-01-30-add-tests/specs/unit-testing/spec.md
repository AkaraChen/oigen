## ADDED Requirements

### Requirement: Test coverage threshold
The test suite SHALL achieve at least 90% code coverage with branch coverage enabled.

#### Scenario: Coverage check passes
- **WHEN** running `pytest --cov=oigen --cov-branch`
- **THEN** the coverage report shows ≥90% total coverage

#### Scenario: CI fails on low coverage
- **WHEN** coverage drops below 90%
- **THEN** the test run SHALL fail with a non-zero exit code

### Requirement: Test reproducibility
All tests involving random generation SHALL produce deterministic results when using a fixed seed.

#### Scenario: Seeded generator produces same output
- **WHEN** a generator test runs with seed=42
- **THEN** running the same test again with seed=42 produces identical output

#### Scenario: Tests use isolated random instances
- **WHEN** multiple tests run in the same session
- **THEN** each test's random state SHALL NOT affect other tests

### Requirement: Error class testing
The test suite SHALL verify all custom exception classes in `errors.py`.

#### Scenario: OigenError stores message and suggestion
- **WHEN** `OigenError("msg", suggestion="hint")` is created
- **THEN** `str(error)` includes both "msg" and "hint"

#### Scenario: OigenError without suggestion
- **WHEN** `OigenError("msg")` is created without suggestion
- **THEN** `str(error)` shows only "msg"

#### Scenario: Subclass inheritance
- **WHEN** `ConstraintError`, `GeneratorError`, `WorkflowError`, `StressTestError` are raised
- **THEN** they SHALL be catchable as `OigenError`

### Requirement: Console output testing
The test suite SHALL verify all Console methods in `output.py` respect verbosity levels.

#### Scenario: Quiet mode suppresses info
- **WHEN** `Console(verbosity=Verbosity.QUIET)` calls `info()`
- **THEN** nothing is printed

#### Scenario: Verbose mode shows debug
- **WHEN** `Console(verbosity=Verbosity.VERBOSE)` calls `debug()`
- **THEN** the debug message is printed

#### Scenario: Error always prints
- **WHEN** `Console(verbosity=Verbosity.QUIET)` calls `error()`
- **THEN** the error message is still printed

#### Scenario: Progress bar creation
- **WHEN** `console.progress()` is called
- **THEN** a context manager is returned that can track progress

### Requirement: Primitive generator testing
The test suite SHALL verify all primitive generators (Int, Double, Char, Bool) in `generators/primitives.py`.

#### Scenario: Int generates within range
- **WHEN** `Int(min_val=1, max_val=10).generate(rng)` is called
- **THEN** the result is an integer where 1 ≤ result ≤ 10

#### Scenario: Int validation rejects invalid range
- **WHEN** `Int(min_val=10, max_val=1).validate()` is called
- **THEN** a `ConstraintError` is raised

#### Scenario: Double respects precision
- **WHEN** `Double(min_val=0, max_val=1, precision=2).generate(rng)` is called
- **THEN** the result has at most 2 decimal places

#### Scenario: Char generates from charset
- **WHEN** `Char(charset="abc").generate(rng)` is called
- **THEN** the result is one of 'a', 'b', or 'c'

#### Scenario: Char validation rejects empty charset
- **WHEN** `Char(charset="").validate()` is called
- **THEN** a `ConstraintError` is raised

#### Scenario: Bool respects probability
- **WHEN** `Bool(true_prob=1.0).generate(rng)` is called 100 times
- **THEN** all results are True

#### Scenario: Bool validation rejects invalid probability
- **WHEN** `Bool(true_prob=1.5).validate()` is called
- **THEN** a `ConstraintError` is raised

### Requirement: Sequence generator testing
The test suite SHALL verify the Sequence generator in `generators/sequence.py`.

#### Scenario: Fixed length sequence
- **WHEN** `Sequence(Int(1,10), length=5).generate(rng)` is called
- **THEN** the result is a list of exactly 5 integers

#### Scenario: Variable length sequence
- **WHEN** `Sequence(Int(1,10), length=(3,7)).generate(rng)` is called
- **THEN** the result length is between 3 and 7 inclusive

#### Scenario: Sequence validation rejects non-generator element
- **WHEN** `Sequence(42, length=5).validate()` is called
- **THEN** a `ConstraintError` is raised

### Requirement: Tree generator testing
The test suite SHALL verify the Tree generator in `generators/tree.py`.

#### Scenario: Tree generates valid edges
- **WHEN** `Tree(n=5).generate(rng)` is called
- **THEN** the result has exactly 4 edges connecting 5 nodes

#### Scenario: Single node tree
- **WHEN** `Tree(n=1).generate(rng)` is called
- **THEN** the result has 0 edges

#### Scenario: Tree with node values
- **WHEN** `Tree(n=3, node_value=Int(1,10)).generate(rng)` is called
- **THEN** the result includes 3 node values

#### Scenario: TreeData string formatting
- **WHEN** `str(tree_data)` is called
- **THEN** the output follows OI-style format (n on first line, edges on subsequent lines)

### Requirement: Graph generator testing
The test suite SHALL verify the Graph generator in `generators/graph.py`.

#### Scenario: Graph generates correct edge count
- **WHEN** `Graph(n=4, m=6).generate(rng)` is called
- **THEN** the result has exactly 6 edges

#### Scenario: Undirected graph max edges
- **WHEN** `Graph(n=4, m=100, allow_multi_edges=False).generate(rng)` is called
- **THEN** the edge count does not exceed n*(n-1)/2

#### Scenario: Directed graph allows more edges
- **WHEN** `Graph(n=4, m=12, directed=True, allow_multi_edges=False).generate(rng)` is called
- **THEN** the edge count does not exceed n*(n-1)

#### Scenario: Self-loops when allowed
- **WHEN** `Graph(n=3, m=10, allow_self_loops=True).generate(rng)` is called multiple times
- **THEN** some edges MAY have u == v

#### Scenario: No self-loops by default
- **WHEN** `Graph(n=3, m=3, allow_self_loops=False).generate(rng)` is called
- **THEN** no edges have u == v

### Requirement: String generator testing
The test suite SHALL verify the String generator in `generators/string.py`.

#### Scenario: Fixed length string
- **WHEN** `String(length=10).generate(rng)` is called
- **THEN** the result string has exactly 10 characters

#### Scenario: Variable length string
- **WHEN** `String(length=(5,15)).generate(rng)` is called
- **THEN** the result length is between 5 and 15 inclusive

#### Scenario: Custom charset
- **WHEN** `String(length=5, charset="01").generate(rng)` is called
- **THEN** the result contains only '0' and '1' characters

#### Scenario: String validation rejects empty charset
- **WHEN** `String(length=5, charset="").validate()` is called
- **THEN** a `ConstraintError` is raised

### Requirement: Matrix generator testing
The test suite SHALL verify the Matrix generator in `generators/matrix.py`.

#### Scenario: Matrix dimensions
- **WHEN** `Matrix(rows=3, cols=4, element=Int(0,9)).generate(rng)` is called
- **THEN** the result is a 3x4 matrix

#### Scenario: Variable dimensions
- **WHEN** `Matrix(rows=(2,5), cols=(3,6), element=Int(0,9)).generate(rng)` is called
- **THEN** the result dimensions are within the specified ranges

#### Scenario: Character matrix formatting
- **WHEN** `str(matrix_data)` is called on a Char-element matrix
- **THEN** the output has no spaces between characters

#### Scenario: Numeric matrix formatting
- **WHEN** `str(matrix_data)` is called on an Int-element matrix
- **THEN** the output has space-separated values

### Requirement: Workflow testing
The test suite SHALL verify the Workflow class in `workflow.py`.

#### Scenario: Generate single output
- **WHEN** `workflow.generate_one()` is called
- **THEN** a single generated value is returned

#### Scenario: Generate multiple files
- **WHEN** `workflow.run(output_dir, count=5)` is called
- **THEN** 5 files are created in the output directory

#### Scenario: Seed reproducibility
- **WHEN** `workflow.run(dir1, count=3, seed=42)` and `workflow.run(dir2, count=3, seed=42)` are called
- **THEN** the generated files have identical content

#### Scenario: Custom formatter
- **WHEN** a Workflow is created with a custom formatter function
- **THEN** `workflow.format(data)` uses that formatter

#### Scenario: Default formatter handles data types
- **WHEN** `default_formatter()` receives TreeData, GraphData, lists, or primitives
- **THEN** it returns appropriate string representations

### Requirement: Stress test testing
The test suite SHALL verify the StressTest class in `stress.py`.

#### Scenario: Detect output mismatch
- **WHEN** std and hack executables produce different outputs for the same input
- **THEN** `StressResult.hacks_found` is incremented and the hack is saved

#### Scenario: Handle timeout
- **WHEN** an executable exceeds the timeout
- **THEN** `StressResult.timeouts` is incremented

#### Scenario: Handle runtime error
- **WHEN** an executable returns non-zero exit code
- **THEN** `StressResult.errors` is incremented

#### Scenario: Early termination
- **WHEN** `stress.run(until_hack=True)` finds a hack
- **THEN** the test stops immediately

#### Scenario: Validate executables exist
- **WHEN** `StressTest` is created with non-existent executable path
- **THEN** a `StressTestError` is raised during validation

### Requirement: Decorator system testing
The test suite SHALL verify the constraint decorator system in `decorators/base.py`.

#### Scenario: Constrained decorator attaches registry
- **WHEN** a function is decorated with `@constrained`
- **THEN** the returned generator has an attached ConstraintRegistry

#### Scenario: Add constraint to registry
- **WHEN** `registry.add(constraint)` is called
- **THEN** `registry.get(ConstraintType)` returns that constraint

#### Scenario: Validate all constraints
- **WHEN** `registry.validate_all(generator)` is called
- **THEN** each constraint's `validate()` method is invoked

#### Scenario: Apply all constraints
- **WHEN** `registry.apply_all(generator, rng)` is called
- **THEN** each constraint's `apply()` method is invoked and context is merged

#### Scenario: Get constraints from generator
- **WHEN** `get_constraints(generator)` is called on a constrained generator
- **THEN** the ConstraintRegistry is returned
