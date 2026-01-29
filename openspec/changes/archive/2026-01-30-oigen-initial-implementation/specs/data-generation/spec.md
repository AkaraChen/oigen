## ADDED Requirements

### Requirement: Workflow decorator for data generation
The system SHALL provide a `@oigen.workflow` decorator that transforms a function into a data generation workflow. The decorated function SHALL define the structure of generated data using generator composition.

#### Scenario: Define a simple workflow
- **WHEN** user decorates a function with `@oigen.workflow`
- **THEN** the function becomes a callable workflow that generates data according to its definition

#### Scenario: Workflow with output path
- **WHEN** user calls `workflow.run(output="path/to/dir", count=10)`
- **THEN** the system generates 10 data files in the specified directory

### Requirement: Integer generator
The system SHALL provide an `Int(min, max)` generator that produces random integers within the specified inclusive range.

#### Scenario: Generate integer in range
- **WHEN** user creates `Int(1, 100)` and calls generate
- **THEN** the result is an integer between 1 and 100 inclusive

#### Scenario: Invalid range raises error
- **WHEN** user creates `Int(100, 1)` where min > max
- **THEN** the system raises a descriptive error

### Requirement: Double generator
The system SHALL provide a `Double(min, max, precision)` generator that produces random floating-point numbers within the specified range with configurable decimal precision.

#### Scenario: Generate double with precision
- **WHEN** user creates `Double(0.0, 1.0, precision=2)` and calls generate
- **THEN** the result is a float like 0.42 with at most 2 decimal places

### Requirement: Char generator
The system SHALL provide a `Char(charset)` generator that produces random characters from the specified character set. Default charset SHALL be lowercase letters.

#### Scenario: Generate lowercase letter
- **WHEN** user creates `Char()` and calls generate
- **THEN** the result is a character from 'a' to 'z'

#### Scenario: Generate from custom charset
- **WHEN** user creates `Char("ABC123")` and calls generate
- **THEN** the result is one of 'A', 'B', 'C', '1', '2', or '3'

### Requirement: Bool generator
The system SHALL provide a `Bool(true_prob)` generator that produces random boolean values with configurable probability of True. Default probability SHALL be 0.5.

#### Scenario: Generate boolean with default probability
- **WHEN** user creates `Bool()` and generates many values
- **THEN** approximately 50% of values are True

#### Scenario: Generate boolean with custom probability
- **WHEN** user creates `Bool(true_prob=0.8)` and generates many values
- **THEN** approximately 80% of values are True

### Requirement: Sequence generator
The system SHALL provide a `Sequence(element, length)` generator that produces a list of elements. Length MAY be a fixed integer or a range tuple.

#### Scenario: Generate fixed-length sequence
- **WHEN** user creates `Sequence(Int(1, 10), length=5)` and calls generate
- **THEN** the result is a list of exactly 5 integers

#### Scenario: Generate variable-length sequence
- **WHEN** user creates `Sequence(Int(1, 10), length=(3, 7))` and calls generate
- **THEN** the result is a list with length between 3 and 7 inclusive

### Requirement: Tree generator
The system SHALL provide a `Tree(n, node_value)` generator that produces a random tree structure with n nodes. Each node MAY have an associated value from the node_value generator.

#### Scenario: Generate tree with n nodes
- **WHEN** user creates `Tree(n=10, node_value=Int(1, 100))` and calls generate
- **THEN** the result is a tree with 10 nodes, each with an integer value

#### Scenario: Generate tree edges
- **WHEN** user generates a tree with n nodes
- **THEN** the output includes n-1 edges representing the tree structure

#### Scenario: Tree connectivity
- **WHEN** user generates a tree
- **THEN** the resulting graph is connected and acyclic

### Requirement: Graph generator
The system SHALL provide a `Graph(n, m, node_value, directed, allow_self_loops, allow_multi_edges)` generator for random graphs with n nodes and m edges.

#### Scenario: Generate undirected simple graph
- **WHEN** user creates `Graph(n=5, m=7)` with defaults
- **THEN** the result is an undirected graph with 5 nodes, 7 edges, no self-loops, no multi-edges

#### Scenario: Generate directed graph
- **WHEN** user creates `Graph(n=5, m=7, directed=True)`
- **THEN** the result is a directed graph with 5 nodes and 7 directed edges

#### Scenario: Edge count validation
- **WHEN** user requests more edges than possible for given constraints
- **THEN** the system raises a descriptive error explaining the maximum allowed edges

### Requirement: Dict generator
The system SHALL provide a `Dict(schema)` generator that produces dictionaries with specified key-value structure.

#### Scenario: Generate dict with schema
- **WHEN** user creates `Dict({"name": Char(), "age": Int(1, 100)})` and calls generate
- **THEN** the result is a dict like `{"name": "x", "age": 42}`

### Requirement: Generator composition
The system SHALL allow generators to be nested arbitrarily to create complex data structures.

#### Scenario: Nested sequence of dicts
- **WHEN** user creates `Sequence(Dict({"x": Int(1, 10)}), length=3)`
- **THEN** the result is a list of 3 dicts, each with an "x" key

#### Scenario: Tree with complex node values
- **WHEN** user creates `Tree(n=5, node_value=Dict({"weight": Int(1, 100), "label": Char()}))`
- **THEN** each tree node has a dict value with weight and label

### Requirement: Reproducible generation with seed
The system SHALL support seeding the random number generator for reproducible data generation.

#### Scenario: Same seed produces same data
- **WHEN** user runs a workflow twice with the same seed
- **THEN** both runs produce identical data

#### Scenario: Default random behavior
- **WHEN** user runs a workflow without specifying a seed
- **THEN** each run produces different random data
