## REMOVED Requirements

### Requirement: Dict generator
**Reason**: Dict 不符合 OI/ACM 场景需求，被 String 生成器替代
**Migration**: 使用 `String` 生成器或直接使用 Python dict 字面量

## MODIFIED Requirements

### Requirement: Tree generator
The system SHALL provide a `Tree(n)` generator that produces a random tree structure with n nodes. The generator SHALL only accept `n` as its core parameter; all weight and structural constraints SHALL be injected via decorators.

#### Scenario: Generate tree with n nodes
- **WHEN** user creates `Tree(n=10)` without decorators
- **THEN** the result is a random tree with 10 nodes and 9 edges

#### Scenario: Tree connectivity
- **WHEN** user generates a tree
- **THEN** the resulting graph is connected and acyclic

### Requirement: Graph generator
The system SHALL provide a `Graph(n, m)` generator for random graphs with n nodes and m edges. The generator SHALL only accept `n` and `m` as core parameters; all other constraints SHALL be injected via decorators.

#### Scenario: Generate undirected simple graph
- **WHEN** user creates `Graph(n=5, m=7)` without decorators
- **THEN** the result is an undirected simple graph with 5 nodes and 7 edges

#### Scenario: Edge count validation
- **WHEN** user requests more edges than possible for a simple graph
- **THEN** the system raises a descriptive error explaining the maximum allowed edges

### Requirement: Sequence generator
The system SHALL provide a `Sequence(element, length)` generator that produces a list of elements. All element relationship constraints SHALL be injected via decorators.

#### Scenario: Generate fixed-length sequence
- **WHEN** user creates `Sequence(Int(1, 10), length=5)` and calls generate
- **THEN** the result is a list of exactly 5 integers

#### Scenario: Generate variable-length sequence
- **WHEN** user creates `Sequence(Int(1, 10), length=(3, 7))` and calls generate
- **THEN** the result is a list with length between 3 and 7 inclusive

## ADDED Requirements

### Requirement: Tree node weight decorator
The system SHALL provide a `@with_node_weight(generator)` decorator that assigns values to tree nodes.

#### Scenario: Tree with node weights
- **WHEN** user applies `@with_node_weight(Int(1, 100))` to a Tree generator
- **THEN** the output includes node weights in addition to edges

### Requirement: Tree edge weight decorator
The system SHALL provide a `@with_edge_weight(generator)` decorator that assigns values to tree edges.

#### Scenario: Tree with edge weights
- **WHEN** user applies `@with_edge_weight(Int(1, 100))` to a Tree generator
- **THEN** the output includes edge weights for each edge

### Requirement: Tree diameter constraint decorator
The system SHALL provide a `@with_diameter(min, max)` decorator that constrains the tree diameter.

#### Scenario: Diameter constraint
- **WHEN** user applies `@with_diameter(5, 8)` to `Tree(n=10)`
- **THEN** the generated tree has diameter between 5 and 8 inclusive

#### Scenario: Invalid diameter error
- **WHEN** user applies `@with_diameter(20)` to `Tree(n=10)`
- **THEN** the system raises a friendly error explaining diameter cannot exceed n-1

### Requirement: Tree centroid constraint decorator
The system SHALL provide a `@with_centroid(count)` decorator that constrains the number of centroids.

#### Scenario: Single centroid
- **WHEN** user applies `@with_centroid(count=1)` to a Tree generator
- **THEN** the generated tree has exactly 1 centroid

#### Scenario: Two centroids
- **WHEN** user applies `@with_centroid(count=2)` to a Tree generator
- **THEN** the generated tree has exactly 2 centroids (adjacent nodes)

### Requirement: Tree depth constraint decorator
The system SHALL provide a `@with_depth(min, max)` decorator that constrains the tree depth (from a designated root).

#### Scenario: Depth constraint
- **WHEN** user applies `@with_depth(min=3, max=5)` to a Tree generator
- **THEN** the generated tree has depth between 3 and 5 when rooted optimally

### Requirement: Graph node weight decorator
The system SHALL provide a `@with_node_weight(generator)` decorator that assigns values to graph nodes.

#### Scenario: Graph with node weights
- **WHEN** user applies `@with_node_weight(Int(1, 100))` to a Graph generator
- **THEN** the output includes node weights

### Requirement: Graph edge weight decorator
The system SHALL provide a `@with_edge_weight(generator)` decorator that assigns values to graph edges.

#### Scenario: Graph with edge weights
- **WHEN** user applies `@with_edge_weight(Int(1, 100))` to a Graph generator
- **THEN** the output includes edge weights for each edge

### Requirement: Directed graph decorator
The system SHALL provide a `@directed` decorator that makes the graph directed.

#### Scenario: Directed graph
- **WHEN** user applies `@directed` to a Graph generator
- **THEN** the generated graph has directed edges

### Requirement: Graph cycle constraint decorator
The system SHALL provide a `@with_cycle(negative)` decorator that ensures the graph contains a cycle.

#### Scenario: Graph with non-negative cycle
- **WHEN** user applies `@with_cycle(negative=False)` with edge weights
- **THEN** the generated graph contains at least one cycle with non-negative total weight

#### Scenario: Graph with negative cycle
- **WHEN** user applies `@with_cycle(negative=True)` with edge weights
- **THEN** the generated graph contains at least one cycle with negative total weight

### Requirement: Graph path constraint decorator
The system SHALL provide a `@with_path(start, end)` decorator that guarantees a path exists between two nodes.

#### Scenario: Guaranteed path
- **WHEN** user applies `@with_path(start=1, end=n)` to a Graph generator
- **THEN** the generated graph has at least one path from node 1 to node n

### Requirement: Graph cut vertex constraint decorator
The system SHALL provide a `@with_cut_vertex(count)` decorator that ensures the graph has a specific number of cut vertices (articulation points).

#### Scenario: Graph with cut vertices
- **WHEN** user applies `@with_cut_vertex(count=2)` to a Graph generator
- **THEN** the generated graph has exactly 2 cut vertices

### Requirement: Graph longest path constraint decorator
The system SHALL provide a `@with_longest_path(min, max)` decorator that constrains the longest simple path length.

#### Scenario: Longest path constraint
- **WHEN** user applies `@with_longest_path(min=5, max=10)` to a Graph generator
- **THEN** the longest simple path in the generated graph has length between 5 and 10

### Requirement: Graph self-loop decorator
The system SHALL provide a `@allow_self_loops` decorator that permits self-loops in the graph.

#### Scenario: Graph with self-loops
- **WHEN** user applies `@allow_self_loops` to a Graph generator
- **THEN** the generated graph may contain edges from a node to itself

### Requirement: Graph multi-edge decorator
The system SHALL provide a `@allow_multi_edges` decorator that permits multiple edges between the same pair of nodes.

#### Scenario: Graph with multi-edges
- **WHEN** user applies `@allow_multi_edges` to a Graph generator
- **THEN** the generated graph may contain multiple edges between the same node pair

### Requirement: Sequence relation constraint decorator
The system SHALL provide a `@with_relation(predicate)` decorator that enforces a relationship between adjacent elements.

#### Scenario: Adjacent difference constraint
- **WHEN** user applies `@with_relation(lambda a, b: abs(a - b) <= 5)` to a Sequence generator
- **THEN** the absolute difference between any two adjacent elements is at most 5

#### Scenario: Custom relation
- **WHEN** user applies `@with_relation(lambda a, b: a < b or a % b == 0)` to a Sequence generator
- **THEN** each adjacent pair satisfies the custom predicate

### Requirement: Sequence monotonic decorator
The system SHALL provide a `@monotonic(direction)` decorator for monotonic sequences.

#### Scenario: Increasing sequence
- **WHEN** user applies `@monotonic(direction='increasing')` to a Sequence generator
- **THEN** each element is greater than or equal to the previous

#### Scenario: Strictly decreasing sequence
- **WHEN** user applies `@monotonic(direction='strictly_decreasing')` to a Sequence generator
- **THEN** each element is strictly less than the previous

### Requirement: Sequence prefix sum constraint decorator
The system SHALL provide a `@prefix_sum_bounded(max_val)` decorator that limits prefix sums.

#### Scenario: Prefix sum bound
- **WHEN** user applies `@prefix_sum_bounded(max_val=100)` to a Sequence generator
- **THEN** the sum of any prefix does not exceed 100

### Requirement: Decorator composition and conflict detection
The system SHALL detect conflicting decorator combinations and raise friendly errors.

#### Scenario: Impossible tree constraints
- **WHEN** user applies `@with_diameter(1)` and `@with_depth(min=5)` to `Tree(n=10)`
- **THEN** the system raises a friendly error explaining these constraints are incompatible

#### Scenario: Graph edge overflow with constraints
- **WHEN** user applies `@with_cycle()` to `Graph(n=3, m=2)` (tree-like)
- **THEN** the system raises a friendly error explaining a cycle requires at least n edges
