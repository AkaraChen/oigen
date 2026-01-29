"""
Tests for oigen.decorators.graph module.
"""

import pytest

from oigen.errors import ConstraintError
from oigen.generators import Int
from oigen.generators.graph import Graph
from oigen.decorators.base import get_constraints, ConstraintRegistry
from oigen.decorators.graph import (
    DirectedConstraint,
    GraphNodeWeightConstraint,
    GraphEdgeWeightConstraint,
    CycleConstraint,
    PathConstraint,
    CutVertexConstraint,
    LongestPathConstraint,
    SelfLoopsConstraint,
    MultiEdgesConstraint,
    directed,
    with_node_weight,
    with_edge_weight,
    with_cycle,
    with_path,
    with_cut_vertex,
    with_longest_path,
    allow_self_loops,
    allow_multi_edges,
)


class TestDirectedConstraint:
    def test_validate(self):
        c = DirectedConstraint()
        c.validate(Graph(n=5, m=7), ConstraintRegistry())  # Always valid

    def test_apply(self):
        c = DirectedConstraint()
        context = {}
        c.apply(Graph(n=5, m=7), context)
        assert context["directed"] is True

    def test_priority(self):
        c = DirectedConstraint()
        assert c.priority == 5


class TestGraphNodeWeightConstraint:
    def test_validate_valid(self):
        c = GraphNodeWeightConstraint(generator=Int(1, 10))
        c.validate(Graph(n=5, m=7), ConstraintRegistry())

    def test_validate_invalid_generator(self):
        c = GraphNodeWeightConstraint(generator=42)  # type: ignore
        with pytest.raises(ConstraintError) as exc_info:
            c.validate(Graph(n=5, m=7), ConstraintRegistry())
        assert "generator must be a BaseGenerator" in str(exc_info.value)

    def test_apply(self):
        c = GraphNodeWeightConstraint(generator=Int(1, 10))
        context = {}
        c.apply(Graph(n=5, m=7), context)
        assert "node_weight" in context


class TestGraphEdgeWeightConstraint:
    def test_validate_valid(self):
        c = GraphEdgeWeightConstraint(generator=Int(1, 10))
        c.validate(Graph(n=5, m=7), ConstraintRegistry())

    def test_validate_invalid_generator(self):
        c = GraphEdgeWeightConstraint(generator="not gen")  # type: ignore
        with pytest.raises(ConstraintError) as exc_info:
            c.validate(Graph(n=5, m=7), ConstraintRegistry())
        assert "generator must be a BaseGenerator" in str(exc_info.value)

    def test_apply(self):
        c = GraphEdgeWeightConstraint(generator=Int(1, 10))
        context = {}
        c.apply(Graph(n=5, m=7), context)
        assert "edge_weight" in context


class TestCycleConstraint:
    def test_validate_valid(self):
        c = CycleConstraint()
        c.validate(Graph(n=5, m=7), ConstraintRegistry())

    def test_validate_not_enough_edges(self):
        c = CycleConstraint()
        with pytest.raises(ConstraintError) as exc_info:
            c.validate(Graph(n=10, m=5), ConstraintRegistry())  # m < n
        assert "cycle" in str(exc_info.value)

    def test_validate_negative_cycle_without_weights(self):
        c = CycleConstraint(negative=True)
        with pytest.raises(ConstraintError) as exc_info:
            c.validate(Graph(n=5, m=7), ConstraintRegistry())
        assert "edge weights" in str(exc_info.value)

    def test_validate_negative_cycle_with_weights(self):
        c = CycleConstraint(negative=True)
        registry = ConstraintRegistry()
        registry.add(GraphEdgeWeightConstraint(generator=Int(-10, 10)))
        c.validate(Graph(n=5, m=7), registry)  # Should pass

    def test_apply(self):
        c = CycleConstraint(negative=True)
        context = {}
        c.apply(Graph(n=5, m=7), context)
        assert context["has_cycle"] is True
        assert context["negative_cycle"] is True


class TestPathConstraint:
    def test_validate_valid(self):
        c = PathConstraint(start=1, end=5)
        c.validate(Graph(n=5, m=7), ConstraintRegistry())

    def test_validate_start_out_of_range(self):
        c = PathConstraint(start=0, end=5)
        with pytest.raises(ConstraintError) as exc_info:
            c.validate(Graph(n=5, m=7), ConstraintRegistry())
        assert "start" in str(exc_info.value)

    def test_validate_start_too_large(self):
        c = PathConstraint(start=10, end=5)
        with pytest.raises(ConstraintError) as exc_info:
            c.validate(Graph(n=5, m=7), ConstraintRegistry())
        assert "start" in str(exc_info.value)

    def test_validate_end_out_of_range(self):
        c = PathConstraint(start=1, end=0)
        with pytest.raises(ConstraintError) as exc_info:
            c.validate(Graph(n=5, m=7), ConstraintRegistry())
        assert "end" in str(exc_info.value)

    def test_validate_end_too_large(self):
        c = PathConstraint(start=1, end=10)
        with pytest.raises(ConstraintError) as exc_info:
            c.validate(Graph(n=5, m=7), ConstraintRegistry())
        assert "end" in str(exc_info.value)

    def test_apply(self):
        c = PathConstraint(start=1, end=5)
        context = {}
        c.apply(Graph(n=5, m=7), context)
        assert context["guaranteed_path"] == (1, 5)


class TestCutVertexConstraint:
    def test_validate_valid(self):
        c = CutVertexConstraint(count=2)
        c.validate(Graph(n=10, m=15), ConstraintRegistry())

    def test_validate_negative_count(self):
        c = CutVertexConstraint(count=-1)
        with pytest.raises(ConstraintError) as exc_info:
            c.validate(Graph(n=10, m=15), ConstraintRegistry())
        assert "negative" in str(exc_info.value)

    def test_validate_count_exceeds_n_minus_2(self):
        c = CutVertexConstraint(count=10)
        with pytest.raises(ConstraintError) as exc_info:
            c.validate(Graph(n=5, m=7), ConstraintRegistry())  # n-2 = 3
        assert "n-2" in str(exc_info.value)

    def test_apply(self):
        c = CutVertexConstraint(count=2)
        context = {}
        c.apply(Graph(n=10, m=15), context)
        assert context["cut_vertex_count"] == 2


class TestLongestPathConstraint:
    def test_validate_valid(self):
        c = LongestPathConstraint(min_val=3, max_val=5)
        c.validate(Graph(n=10, m=15), ConstraintRegistry())

    def test_validate_min_less_than_1(self):
        c = LongestPathConstraint(min_val=0, max_val=5)
        with pytest.raises(ConstraintError) as exc_info:
            c.validate(Graph(n=10, m=15), ConstraintRegistry())
        assert "min" in str(exc_info.value)

    def test_validate_min_greater_than_max(self):
        c = LongestPathConstraint(min_val=5, max_val=3)
        with pytest.raises(ConstraintError) as exc_info:
            c.validate(Graph(n=10, m=15), ConstraintRegistry())
        assert "min" in str(exc_info.value) and "max" in str(exc_info.value)

    def test_validate_min_exceeds_n(self):
        c = LongestPathConstraint(min_val=10, max_val=15)
        with pytest.raises(ConstraintError) as exc_info:
            c.validate(Graph(n=5, m=7), ConstraintRegistry())
        assert "n-1" in str(exc_info.value)

    def test_apply(self):
        c = LongestPathConstraint(min_val=3, max_val=5)
        context = {}
        c.apply(Graph(n=10, m=15), context)
        assert context["longest_path"] == (3, 5)


class TestSelfLoopsConstraint:
    def test_validate(self):
        c = SelfLoopsConstraint()
        c.validate(Graph(n=5, m=7), ConstraintRegistry())  # Always valid

    def test_apply(self):
        c = SelfLoopsConstraint()
        context = {}
        c.apply(Graph(n=5, m=7), context)
        assert context["allow_self_loops"] is True


class TestMultiEdgesConstraint:
    def test_validate(self):
        c = MultiEdgesConstraint()
        c.validate(Graph(n=5, m=7), ConstraintRegistry())  # Always valid

    def test_apply(self):
        c = MultiEdgesConstraint()
        context = {}
        c.apply(Graph(n=5, m=7), context)
        assert context["allow_multi_edges"] is True


class TestDecoratorFunctions:
    def test_directed(self):
        @directed
        def constrained():
            return Graph(n=5, m=7)

        registry = get_constraints(constrained)
        assert registry is not None
        assert registry.has(DirectedConstraint)

    def test_with_node_weight(self):
        @with_node_weight(Int(1, 100))
        def constrained():
            return Graph(n=5, m=7)

        registry = get_constraints(constrained)
        assert registry is not None
        assert registry.has(GraphNodeWeightConstraint)

    def test_with_edge_weight(self):
        @with_edge_weight(Int(1, 100))
        def constrained():
            return Graph(n=5, m=7)

        registry = get_constraints(constrained)
        assert registry is not None
        assert registry.has(GraphEdgeWeightConstraint)

    def test_with_cycle(self):
        @with_cycle()
        def constrained():
            return Graph(n=5, m=7)

        registry = get_constraints(constrained)
        assert registry is not None
        assert registry.has(CycleConstraint)

    def test_with_path(self):
        @with_path(1, 5)
        def constrained():
            return Graph(n=5, m=7)

        registry = get_constraints(constrained)
        assert registry is not None
        c = registry.get_one(PathConstraint)
        assert c is not None
        assert c.start == 1
        assert c.end == 5

    def test_with_cut_vertex(self):
        @with_cut_vertex(2)
        def constrained():
            return Graph(n=10, m=15)

        registry = get_constraints(constrained)
        assert registry is not None
        assert registry.has(CutVertexConstraint)

    def test_with_longest_path_range(self):
        @with_longest_path(3, 5)
        def constrained():
            return Graph(n=10, m=15)

        registry = get_constraints(constrained)
        c = registry.get_one(LongestPathConstraint)
        assert c is not None
        assert c.min_val == 3
        assert c.max_val == 5

    def test_with_longest_path_exact(self):
        @with_longest_path(4)
        def constrained():
            return Graph(n=10, m=15)

        registry = get_constraints(constrained)
        c = registry.get_one(LongestPathConstraint)
        assert c is not None
        assert c.min_val == 4
        assert c.max_val == 4

    def test_allow_self_loops(self):
        @allow_self_loops
        def constrained():
            return Graph(n=5, m=7)

        registry = get_constraints(constrained)
        assert registry is not None
        assert registry.has(SelfLoopsConstraint)

    def test_allow_multi_edges(self):
        @allow_multi_edges
        def constrained():
            return Graph(n=5, m=7)

        registry = get_constraints(constrained)
        assert registry is not None
        assert registry.has(MultiEdgesConstraint)
