"""
oigen - OI/ACM test data generation framework

A declarative workflow-based data generation system with stress testing support.

Example:
    from oigen import workflow, Sequence, Int, StressTest

    @workflow
    def my_data():
        return Sequence(Int(1, 100), length=10)

    # Generate 10 test files
    my_data.run(output="./data", count=10)

    # Or stress test two solutions
    stress = StressTest(my_data, std="./std", hack="./hack")
    stress.run(max_iterations=1000)

With constraints:
    from oigen import workflow, Tree, Int, with_diameter, with_edge_weight

    @with_diameter(5, 8)
    @with_edge_weight(Int(1, 100))
    def constrained_tree():
        return Tree(n=10)
"""

__version__ = "0.1.0"

# Generators
from oigen.generators import (
    BaseGenerator,
    Int,
    Double,
    Char,
    Bool,
    Sequence,
    Tree,
    Graph,
)

# New generators
from oigen.generators.string import String, StringData
from oigen.generators.matrix import Matrix, MatrixData

# Data structures
from oigen.generators.tree import TreeData
from oigen.generators.graph import GraphData

# Workflow
from oigen.workflow import workflow, Workflow

# Stress testing
from oigen.stress import StressTest, StressResult

# Errors
from oigen.errors import (
    OigenError,
    ConstraintError,
    GeneratorError,
    WorkflowError,
    StressTestError,
)

# Output utilities
from oigen.output import (
    console,
    Verbosity,
    set_verbosity,
)

# Constraint decorators
from oigen.decorators import (
    # Tree decorators
    with_node_weight,
    with_edge_weight,
    with_diameter,
    with_centroid,
    with_depth,
    # Graph decorators
    directed,
    with_cycle,
    with_path,
    with_cut_vertex,
    with_longest_path,
    allow_self_loops,
    allow_multi_edges,
    # Sequence decorators
    with_relation,
    monotonic,
    prefix_sum_bounded,
    # String decorators
    from_charset,
    from_template,
    must_contain,
    as_trie_words,
    # Matrix decorators
    as_maze,
    with_path_between,
    with_border,
    with_coord_constraint,
    row_sum_max,
    col_sum_max,
    row_product_max,
    col_product_max,
    with_row_operator,
    with_col_operator,
)

__all__ = [
    # Version
    "__version__",
    # Generators
    "BaseGenerator",
    "Int",
    "Double",
    "Char",
    "Bool",
    "Sequence",
    "Tree",
    "Graph",
    "String",
    "Matrix",
    # Data structures
    "TreeData",
    "GraphData",
    "StringData",
    "MatrixData",
    # Workflow
    "workflow",
    "Workflow",
    # Stress testing
    "StressTest",
    "StressResult",
    # Errors
    "OigenError",
    "ConstraintError",
    "GeneratorError",
    "WorkflowError",
    "StressTestError",
    # Output
    "console",
    "Verbosity",
    "set_verbosity",
    # Tree decorators
    "with_node_weight",
    "with_edge_weight",
    "with_diameter",
    "with_centroid",
    "with_depth",
    # Graph decorators
    "directed",
    "with_cycle",
    "with_path",
    "with_cut_vertex",
    "with_longest_path",
    "allow_self_loops",
    "allow_multi_edges",
    # Sequence decorators
    "with_relation",
    "monotonic",
    "prefix_sum_bounded",
    # String decorators
    "from_charset",
    "from_template",
    "must_contain",
    "as_trie_words",
    # Matrix decorators
    "as_maze",
    "with_path_between",
    "with_border",
    "with_coord_constraint",
    "row_sum_max",
    "col_sum_max",
    "row_product_max",
    "col_product_max",
    "with_row_operator",
    "with_col_operator",
]
