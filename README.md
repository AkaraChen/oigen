# oigen

![oigen](https://socialify.git.ci/AkaraChen/oigen/image?language=1&name=1&owner=1&pattern=Brick+Wall&theme=Light)

**OI/ACM test data generation framework with stress testing support.**

oigen provides a declarative, composable approach to generating test data for competitive programming problems. Define your data structure once, apply constraints via decorators, and generate thousands of test cases with reproducible results.

## Philosophy

### Declarative Over Imperative

Instead of writing loops and conditionals to generate data, you describe *what* you want:

```python
# Imperative (traditional approach)
import random
def generate():
    n = random.randint(5, 15)
    edges = []
    for i in range(2, n + 1):
        parent = random.randint(1, i - 1)
        edges.append((parent, i))
    return n, edges

# Declarative (oigen approach)
@workflow
def generate():
    return Tree(n=Int(5, 15))
```

### Composable Constraints

Constraints are applied via decorators, making them reusable and stackable:

```python
@with_diameter(5, 8)           # Structural constraint
@with_edge_weight(Int(1, 100)) # Data constraint
@workflow
def tree_data():
    return Tree(n=10)
```

### Reproducibility First

All generation uses explicit `Random` instances with optional seeding. The same seed always produces the same output:

```python
tree_data.run(output="./tests", count=10, seed=42)  # Always reproducible
```

### OI-Style Output

Output is automatically formatted for competitive programming:
- Numbers separated by spaces and newlines
- Trees output as `n` followed by edges
- Graphs output as `n m` followed by edges
- No trailing spaces, consistent newlines

## Installation

```bash
pip install oigen
# or with pdm
pdm add oigen
```

## Quick Start

```python
from oigen import workflow, Sequence, Int

@workflow
def array_sum():
    """Generate test data for an array sum problem."""
    return Sequence(Int(1, 1000), length=(5, 20))

# Generate 10 test files
array_sum.run(output="./tests", count=10)
```

Output file example (`1.in`):
```
156 872 43 991 234 567 88 12 445
```

## Core Concepts

### Generators

Generators are the building blocks. They produce random values following specific rules.

#### Primitive Generators

```python
from oigen import Int, Double, Char, Bool

Int(1, 100)              # Random integer from 1 to 100
Int()                    # Default: 0 to 10^9
Double(0.0, 1.0)         # Random float
Double(0, 100, precision=2)  # Float with 2 decimal places
Char()                   # Random lowercase letter
Char("ABC123")           # Random char from custom charset
Bool()                   # 50% True, 50% False
Bool(true_prob=0.8)      # 80% True
```

#### Sequence Generator

```python
from oigen import Sequence, Int

Sequence(Int(1, 100), length=10)       # Fixed length of 10
Sequence(Int(1, 100), length=(5, 20))  # Variable length 5-20
```

#### Tree Generator

```python
from oigen import Tree, Int

Tree(n=10)                              # Tree with 10 nodes
Tree(n=Int(5, 15))                      # Variable node count
Tree(n=10, node_value=Int(1, 100))      # With node values
```

Output format:
```
10
45 23 78 12 89 34 56 67 90 11    <- node values (if specified)
1 2
1 3
2 4
...                              <- edges (parent child)
```

#### Graph Generator

```python
from oigen import Graph, Int

Graph(n=5, m=7)                          # 5 nodes, 7 edges
Graph(n=5, m=7, directed=True)           # Directed graph
Graph(n=Int(5, 10), m=Int(10, 20))       # Variable sizes
Graph(n=5, m=20, allow_multi_edges=True) # Allow parallel edges
Graph(n=5, m=10, allow_self_loops=True)  # Allow self-loops
```

Output format:
```
5 7
1 2
3 1
2 4
...
```

#### String Generator

```python
from oigen import String

String(length=10)                    # 10 lowercase letters
String(length=(5, 15))               # Variable length
String(length=10, charset="abc")     # Only 'a', 'b', 'c'
```

#### Matrix Generator

```python
from oigen import Matrix, Int

Matrix(rows=5, cols=5, element=Int(1, 10))   # 5x5 numeric matrix
Matrix(rows=(3, 8), cols=(3, 8), element=Int(0, 1))  # Variable size
```

Output format:
```
5 5
3 7 2 9 1
8 4 6 3 5
...
```

### Workflow

A workflow wraps a generator and handles batch generation:

```python
from oigen import workflow, Sequence, Int

@workflow
def my_data():
    return Sequence(Int(1, 100), length=10)

# Generate files
my_data.run(
    output="./tests",           # Output directory
    count=10,                   # Number of files
    seed=42,                    # Optional seed for reproducibility
    filename_pattern="{n}.in"   # Filename template
)

# Single generation (useful for testing)
from random import Random
data = my_data.generate_one(Random(42))
```

### Custom Formatters

Override the default output format:

```python
def custom_formatter(data):
    """First line: length, Second line: space-separated values."""
    return f"{len(data)}\n{' '.join(str(x) for x in data)}"

@workflow(formatter=custom_formatter)
def formatted_data():
    return Sequence(Int(1, 100), length=10)
```

## Constraint Decorators

Constraints modify generator behavior without changing the generator itself.

### Tree Constraints

```python
from oigen import (
    workflow, Tree, Int,
    with_diameter, with_depth, with_centroid,
    with_node_weight, with_edge_weight
)

# Tree with diameter between 5 and 8 edges
@with_diameter(5, 8)
@workflow
def long_tree():
    return Tree(n=20)

# Tree with specific depth
@with_depth(3, 5)
@workflow
def shallow_tree():
    return Tree(n=15)

# Tree with exactly 1 centroid (balanced-ish)
@with_centroid(1)
@workflow
def balanced_tree():
    return Tree(n=10)

# Weighted tree (both nodes and edges)
@with_node_weight(Int(1, 100))
@with_edge_weight(Int(1, 50))
@workflow
def weighted_tree():
    return Tree(n=10)
```

### Graph Constraints

```python
from oigen import (
    workflow, Graph, Int,
    directed, with_cycle, with_path, with_cut_vertex,
    with_longest_path, allow_self_loops, allow_multi_edges
)

# Directed graph
@directed
@workflow
def dag():
    return Graph(n=10, m=15)

# Graph guaranteed to have a cycle
@with_cycle()
@workflow
def cyclic():
    return Graph(n=10, m=15)

# Graph with negative cycle (for Bellman-Ford testing)
@with_cycle(negative=True)
@with_edge_weight(Int(-10, 10))
@workflow
def negative_cycle():
    return Graph(n=10, m=15)

# Guaranteed path from node 1 to node n
@with_path(1, 10)
@workflow
def connected():
    return Graph(n=10, m=15)

# Graph with exactly 2 articulation points
@with_cut_vertex(2)
@workflow
def with_cuts():
    return Graph(n=10, m=12)
```

### Sequence Constraints

```python
from oigen import (
    workflow, Sequence, Int,
    monotonic, with_relation, prefix_sum_bounded
)

# Strictly increasing sequence
@monotonic("increasing")
@workflow
def sorted_array():
    return Sequence(Int(1, 100), length=10)

# Non-decreasing (allows equal adjacent elements)
@monotonic("non_decreasing", strict=False)
@workflow
def non_decreasing():
    return Sequence(Int(1, 100), length=10)

# Adjacent elements differ by at most 5
@with_relation(lambda a, b: abs(a - b) <= 5)
@workflow
def smooth_array():
    return Sequence(Int(1, 100), length=10)

# All prefix sums <= 1000
@prefix_sum_bounded(1000)
@workflow
def bounded_prefix():
    return Sequence(Int(1, 100), length=20)
```

### String Constraints

```python
from oigen import (
    workflow, String,
    from_charset, from_template, must_contain, as_trie_words
)

# Only use characters 'a', 'b', 'c'
@from_charset("abc")
@workflow
def simple_string():
    return String(length=20)

# Template-based: * is wildcard, others are literal
@from_template("ab*cd*ef*")
@from_charset("xyz")
@workflow
def template_string():
    return String(length=15)

# Must contain specific substrings
@must_contain("abc", "xyz")
@workflow
def containing_string():
    return String(length=30)

# Generate word set for trie problems
@as_trie_words(count=10, max_depth=5)
@from_charset("abc")
@workflow
def trie_words():
    return String()
```

### Matrix Constraints

```python
from oigen import (
    workflow, Matrix, Int,
    as_maze, with_path_between, with_border,
    row_sum_max, col_sum_max, with_coord_constraint
)

# Maze with guaranteed path
@with_path_between((0, 0), (9, 9))
@as_maze(path=".", wall="#")
@workflow
def solvable_maze():
    return Matrix(rows=10, cols=10)

# Maze with border
@with_border("#")
@as_maze()
@workflow
def bordered_maze():
    return Matrix(rows=10, cols=10)

# Matrix with row sum constraint
@row_sum_max(100)
@workflow
def bounded_rows():
    return Matrix(rows=5, cols=5, element=Int(1, 30))

# Custom coordinate-based constraint
@with_coord_constraint(lambda r, c, v: r + c < 5 or v > 3)
@workflow
def diagonal_constraint():
    return Matrix(rows=5, cols=5, element=Int(1, 10))
```

## Use Cases

### Classic Array Problems

```python
@workflow
def array_sum_data():
    """Test data for array sum/max/min problems."""
    return Sequence(Int(-10**9, 10**9), length=(1, 10**5))

@monotonic("increasing")
@workflow
def binary_search_data():
    """Sorted array for binary search problems."""
    return Sequence(Int(1, 10**9), length=(1, 10**5))

@workflow
def two_pointer_data():
    """Data for two-pointer technique problems."""
    return Sequence(Int(1, 1000), length=(10, 1000))
```

### Graph Algorithm Problems

```python
@workflow
def shortest_path_data():
    """Weighted graph for Dijkstra/Bellman-Ford."""
    return Graph(n=Int(2, 1000), m=Int(1, 5000))

@directed
@workflow
def topological_sort_data():
    """DAG for topological sorting."""
    return Graph(n=Int(2, 1000), m=Int(1, 3000))

@with_cycle(negative=True)
@with_edge_weight(Int(-100, 100))
@workflow
def negative_cycle_detection():
    """Graph with negative cycle for SPFA testing."""
    return Graph(n=Int(2, 500), m=Int(500, 2000))
```

### Tree Problems

```python
@with_node_weight(Int(1, 10**6))
@workflow
def tree_dp_data():
    """Weighted tree for tree DP problems."""
    return Tree(n=Int(2, 10**5))

@with_diameter(10, 20)
@workflow
def tree_diameter_data():
    """Tree with specific diameter for path problems."""
    return Tree(n=Int(50, 100))

@with_depth(1, 3)
@workflow
def shallow_tree_data():
    """Shallow tree (chain-like) for edge cases."""
    return Tree(n=Int(10, 100))
```

### String Problems

```python
@from_charset("ab")
@workflow
def palindrome_data():
    """Binary string for palindrome problems."""
    return String(length=(1, 1000))

@as_trie_words(count=100, max_depth=10)
@from_charset("abcdefghij")
@workflow
def trie_data():
    """Word set for trie/AC automaton problems."""
    return String()

@must_contain("pattern")
@workflow
def kmp_data():
    """String guaranteed to contain pattern for KMP testing."""
    return String(length=(20, 1000))
```

### Matrix/Grid Problems

```python
@with_path_between((0, 0), (99, 99))
@as_maze()
@workflow
def bfs_maze_data():
    """Solvable maze for BFS shortest path."""
    return Matrix(rows=100, cols=100)

@row_sum_max(1000)
@col_sum_max(1000)
@workflow
def matrix_dp_data():
    """Constrained matrix for DP problems."""
    return Matrix(rows=100, cols=100, element=Int(0, 100))
```

## Stress Testing

Find bugs by comparing two solutions:

```python
from oigen import workflow, Sequence, Int, StressTest

@workflow
def stress_data():
    return Sequence(Int(1, 10**8), length=(10, 50))

# Compare correct solution (std) against potentially buggy one (hack)
stress = StressTest(
    stress_data,
    std="./std",       # Correct solution executable
    hack="./hack",     # Solution to test
    output="./hacks",  # Where to save failing cases
    timeout=2.0        # Timeout per run in seconds
)

# Run until finding a hack or reaching max iterations
result = stress.run(max_iterations=1000)

# Or run until a hack is found
result = stress.run(until_hack=True)

print(f"Hacks found: {result.hacks_found}")
print(f"Saved to: {result.hack_files}")
```

### Example: Finding Integer Overflow

`std.cpp` (correct):
```cpp
#include <iostream>
using namespace std;
int main() {
    int n; cin >> n;
    long long sum = 0;
    for (int i = 0; i < n; i++) {
        int x; cin >> x;
        sum += x;
    }
    cout << sum << endl;
}
```

`hack.cpp` (buggy - integer overflow):
```cpp
#include <iostream>
using namespace std;
int main() {
    int n; cin >> n;
    int sum = 0;  // Bug: should be long long
    for (int i = 0; i < n; i++) {
        int x; cin >> x;
        sum += x;
    }
    cout << sum << endl;
}
```

```python
@workflow
def overflow_data():
    """Large values to trigger overflow."""
    return Sequence(Int(10**7, 10**8), length=(10, 50))

stress = StressTest(overflow_data, std="./std", hack="./hack")
result = stress.run(max_iterations=100)  # Will likely find overflow quickly
```

## Advanced Usage

### Nested Generators

Generators can be composed:

```python
@workflow
def nested_data():
    """Multiple test cases in one file."""
    n = Int(1, 10)
    return {
        "n": n,
        "arrays": Sequence(
            Sequence(Int(1, 100), length=(5, 10)),
            length=n
        )
    }
```

### Dynamic Parameters

Use generators for parameters:

```python
@workflow
def dynamic_tree():
    """Tree where n determines complexity."""
    n = Int(5, 100)
    return Tree(n=n, node_value=Int(1, n))  # node values scale with n
```

### Stacking Multiple Constraints

Constraints are applied bottom-up (innermost first):

```python
@with_diameter(5, 10)         # Applied 3rd: structural
@with_centroid(1)             # Applied 2nd: structural
@with_edge_weight(Int(1, 100)) # Applied 1st: adds weights
@workflow
def complex_tree():
    return Tree(n=20)
```

### Verbosity Control

Control output verbosity:

```python
from oigen import set_verbosity, Verbosity

set_verbosity(Verbosity.QUIET)    # Minimal output
set_verbosity(Verbosity.DEFAULT)  # Normal output
set_verbosity(Verbosity.VERBOSE)  # Detailed output
```

### Workflow Without Decorator

Create workflows programmatically:

```python
from oigen import Workflow, Sequence, Int

gen = Sequence(Int(1, 100), length=10)
wf = Workflow(gen, name="manual_workflow")
wf.run(output="./tests", count=5)
```

## API Reference

### Generators

| Generator | Description | Parameters |
|-----------|-------------|------------|
| `Int` | Random integer | `min_val`, `max_val` |
| `Double` | Random float | `min_val`, `max_val`, `precision` |
| `Char` | Random character | `charset` |
| `Bool` | Random boolean | `true_prob` |
| `Sequence` | List of elements | `element`, `length` |
| `Tree` | Random tree | `n`, `node_value` |
| `Graph` | Random graph | `n`, `m`, `directed`, `allow_self_loops`, `allow_multi_edges` |
| `String` | Random string | `length`, `charset` |
| `Matrix` | 2D matrix | `rows`, `cols`, `element` |

### Constraint Decorators

| Category | Decorators |
|----------|------------|
| Tree | `with_diameter`, `with_depth`, `with_centroid`, `with_node_weight`, `with_edge_weight` |
| Graph | `directed`, `with_cycle`, `with_path`, `with_cut_vertex`, `with_longest_path`, `allow_self_loops`, `allow_multi_edges` |
| Sequence | `monotonic`, `with_relation`, `prefix_sum_bounded` |
| String | `from_charset`, `from_template`, `must_contain`, `as_trie_words` |
| Matrix | `as_maze`, `with_path_between`, `with_border`, `row_sum_max`, `col_sum_max`, `with_coord_constraint` |

## Development

```bash
# Install dev dependencies
make dev

# Run tests
make test

# Run tests with coverage
make cov

# Lint
make lint

# Format
make fmt
```

## License

MIT
