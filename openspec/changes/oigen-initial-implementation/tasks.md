## 1. Project Setup

- [x] 1.1 Initialize Python package structure with pyproject.toml (Python 3.10+)
- [x] 1.2 Create oigen/ directory with __init__.py exposing public API
- [x] 1.3 Add rich as dependency in pyproject.toml
- [x] 1.4 Create errors.py with base OigenError exception class

## 2. Terminal Output Module

- [x] 2.1 Create output.py with Console wrapper around rich
- [x] 2.2 Implement error() function with red color and ❌ emoji
- [x] 2.3 Implement success() function with green color and ✅ emoji
- [x] 2.4 Implement warning() function with yellow color and ⚠️ emoji
- [x] 2.5 Implement info() function with 💡 emoji
- [x] 2.6 Add terminal capability detection for graceful fallback
- [x] 2.7 Add verbosity level support (default, verbose, quiet)

## 3. Base Generator Framework

- [x] 3.1 Create generators/__init__.py with BaseGenerator abstract class
- [x] 3.2 Define generate(rng: Random) -> Any abstract method
- [x] 3.3 Add validation hooks for constraint checking

## 4. Primitive Generators

- [x] 4.1 Create generators/primitives.py
- [x] 4.2 Implement Int(min, max) generator with range validation
- [x] 4.3 Implement Double(min, max, precision) generator
- [x] 4.4 Implement Char(charset) generator with default lowercase
- [x] 4.5 Implement Bool(true_prob) generator with default 0.5
- [x] 4.6 Add friendly error messages for invalid constraints (e.g., min > max)

## 5. Sequence Generator

- [x] 5.1 Create generators/sequence.py
- [x] 5.2 Implement Sequence(element, length) supporting fixed length
- [x] 5.3 Support length as tuple (min, max) for variable length
- [x] 5.4 Validate that element is a valid generator

## 6. Tree Generator

- [x] 6.1 Create generators/tree.py
- [x] 6.2 Implement Tree(n, node_value) generator
- [x] 6.3 Generate random tree structure with n-1 edges
- [x] 6.4 Ensure generated tree is connected and acyclic
- [x] 6.5 Support optional node_value generator for node data

## 7. Graph Generator

- [x] 7.1 Create generators/graph.py
- [x] 7.2 Implement Graph(n, m) for undirected simple graphs
- [x] 7.3 Add directed parameter for directed graphs
- [x] 7.4 Add allow_self_loops parameter
- [x] 7.5 Add allow_multi_edges parameter
- [x] 7.6 Validate edge count against maximum possible edges
- [x] 7.7 Add friendly error suggesting allow_multi_edges when edge count exceeds limit

## 8. Dict Generator

- [x] 8.1 Create generators/dict.py
- [x] 8.2 Implement Dict(schema) where schema maps keys to generators
- [x] 8.3 Validate all schema values are generators

## 9. Workflow System

- [x] 9.1 Create workflow.py with @workflow decorator
- [x] 9.2 Implement Workflow class to hold generator definition
- [x] 9.3 Add run(output, count) method to generate multiple files
- [x] 9.4 Add seed parameter for reproducible generation
- [x] 9.5 Implement default text formatter for output
- [x] 9.6 Support custom formatter function in workflow definition
- [x] 9.7 Add progress bar during multi-file generation

## 10. Stress Testing

- [x] 10.1 Create stress.py with StressTest class
- [x] 10.2 Implement __init__(workflow, std, hack, output) constructor
- [x] 10.3 Add run(max_iterations) method for bounded stress testing
- [x] 10.4 Add run(until_hack=True) mode for unbounded testing
- [x] 10.5 Implement subprocess execution for std and hack
- [x] 10.6 Add configurable timeout with default 5 seconds
- [x] 10.7 Implement output comparison with whitespace normalization
- [x] 10.8 Save failing inputs to output/hack_{n}.in
- [x] 10.9 Save both outputs (hack_{n}.std.out, hack_{n}.hack.out)
- [x] 10.10 Handle runtime errors (non-zero exit codes)
- [x] 10.11 Add live progress display during stress testing
- [x] 10.12 Show summary on completion (iterations, hacks, time)

## 11. Public API Export

- [x] 11.1 Export workflow decorator from oigen/__init__.py
- [x] 11.2 Export all generators (Int, Double, Char, Bool, Sequence, Tree, Graph, Dict)
- [x] 11.3 Export StressTest class
- [x] 11.4 Ensure clean `from oigen import *` experience

## 12. Integration Testing

- [x] 12.1 Create example workflow that generates sequence data
- [x] 12.2 Create example workflow that generates tree data
- [x] 12.3 Create example workflow that generates graph data
- [x] 12.4 Test stress testing with simple std/hack pair
- [x] 12.5 Verify error messages display correctly with colors and emoji
