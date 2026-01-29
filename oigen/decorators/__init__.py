"""
Constraint decorators for oigen generators.

Decorators can be stacked to add multiple constraints:

    @with_diameter(5, 8)
    @with_edge_weight(Int(1, 100))
    def my_tree():
        return Tree(n=10)

Decorators are applied bottom-up (closest to function first).
"""

from oigen.decorators.base import (
    Constraint,
    ConstraintRegistry,
    constrained,
    get_constraints,
)
from oigen.decorators.graph import (
    allow_multi_edges,
    allow_self_loops,
    directed,
    with_cut_vertex,
    with_cycle,
    with_longest_path,
    with_path,
)
from oigen.decorators.matrix import (
    as_maze,
    col_product_max,
    col_sum_max,
    row_product_max,
    row_sum_max,
    with_border,
    with_col_operator,
    with_coord_constraint,
    with_path_between,
    with_row_operator,
)
from oigen.decorators.sequence import (
    monotonic,
    prefix_sum_bounded,
    with_relation,
)
from oigen.decorators.string import (
    as_trie_words,
    from_charset,
    from_template,
    must_contain,
)
from oigen.decorators.tree import (
    with_centroid,
    with_depth,
    with_diameter,
    with_edge_weight,
    with_node_weight,
)

__all__ = [
    # Base
    "Constraint",
    "ConstraintRegistry",
    "constrained",
    "get_constraints",
    # Tree
    "with_node_weight",
    "with_edge_weight",
    "with_diameter",
    "with_centroid",
    "with_depth",
    # Graph
    "directed",
    "with_cycle",
    "with_path",
    "with_cut_vertex",
    "with_longest_path",
    "allow_self_loops",
    "allow_multi_edges",
    # Sequence
    "with_relation",
    "monotonic",
    "prefix_sum_bounded",
    # String
    "from_charset",
    "from_template",
    "must_contain",
    "as_trie_words",
    # Matrix
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
