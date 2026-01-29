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
# Constraint decorators
from oigen.decorators import (
    allow_multi_edges,
    allow_self_loops,
    # Matrix decorators
    as_maze,
    as_trie_words,
    col_product_max,
    col_sum_max,
    # Graph decorators
    directed,
    # String decorators
    from_charset,
    from_template,
    monotonic,
    must_contain,
    prefix_sum_bounded,
    row_product_max,
    row_sum_max,
    with_border,
    with_centroid,
    with_col_operator,
    with_coord_constraint,
    with_cut_vertex,
    with_cycle,
    with_depth,
    with_diameter,
    with_edge_weight,
    with_longest_path,
    # Tree decorators
    with_node_weight,
    with_path,
    with_path_between,
    # Sequence decorators
    with_relation,
    with_row_operator,
)

# Errors
from oigen.errors import (
    ConstraintError,
    GeneratorError,
    OigenError,
    StressTestError,
    WorkflowError,
)
from oigen.generators import (
    BaseGenerator,
    Bool,
    Char,
    Double,
    Graph,
    Int,
    Sequence,
    Tree,
)
from oigen.generators.graph import GraphData
from oigen.generators.matrix import Matrix, MatrixData

# New generators
from oigen.generators.string import String, StringData

# Data structures
from oigen.generators.tree import TreeData

# Output utilities
from oigen.output import (
    Verbosity,
    console,
    set_verbosity,
)

# Stress testing
from oigen.stress import StressResult, StressTest

# Workflow
from oigen.workflow import Workflow, workflow

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
