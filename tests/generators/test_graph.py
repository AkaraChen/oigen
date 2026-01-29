"""
Tests for oigen.generators.graph module.
"""

from random import Random

import pytest

from oigen.errors import ConstraintError
from oigen.generators import Int
from oigen.generators.graph import Graph, GraphData


class TestGraphData:
    def test_str_format_basic(self):
        data = GraphData(n=3, m=2, edges=[(1, 2), (2, 3)])
        s = str(data)
        lines = s.strip().split("\n")
        assert lines[0] == "3 2"  # n m
        assert len(lines) == 3  # n m + 2 edges

    def test_str_format_with_node_values(self):
        data = GraphData(n=3, m=2, edges=[(1, 2), (2, 3)], node_values=[None, 10, 20, 30])
        s = str(data)
        lines = s.strip().split("\n")
        assert lines[0] == "3 2"  # n m
        assert lines[1] == "10 20 30"  # node values
        assert len(lines) == 4

    def test_str_format_no_edges(self):
        data = GraphData(n=3, m=0, edges=[])
        s = str(data)
        assert s.strip() == "3 0"


class TestGraph:
    def test_generate_correct_edge_count(self, rng):
        gen = Graph(n=5, m=7)
        result = gen.generate(rng)
        assert result.n == 5
        assert result.m == 7
        assert len(result.edges) == 7

    def test_generate_no_edges(self, rng):
        gen = Graph(n=5, m=0)
        result = gen.generate(rng)
        assert len(result.edges) == 0

    def test_generate_deterministic(self):
        gen = Graph(n=5, m=5)
        rng1 = Random(42)
        rng2 = Random(42)
        result1 = gen.generate(rng1)
        result2 = gen.generate(rng2)
        assert result1.edges == result2.edges

    def test_generate_valid_edges(self, rng):
        gen = Graph(n=5, m=7)
        result = gen.generate(rng)
        for u, v in result.edges:
            assert 1 <= u <= 5
            assert 1 <= v <= 5

    def test_undirected_no_self_loops_by_default(self, rng):
        gen = Graph(n=5, m=10)
        for _ in range(10):
            result = gen.generate(rng)
            for u, v in result.edges:
                assert u != v

    def test_undirected_max_edges(self, rng):
        # For n=4, max simple undirected edges = 4*3/2 = 6
        gen = Graph(n=4, m=6)
        result = gen.generate(rng)
        assert len(result.edges) == 6

    def test_undirected_exceeds_max_edges_raises(self):
        # n=4, max = 6, requesting 7
        with pytest.raises(ConstraintError) as exc_info:
            gen = Graph(n=4, m=7)
            gen.generate(Random(42))
        assert "maximum" in str(exc_info.value)

    def test_directed_allows_more_edges(self, rng):
        # For n=4, directed max = 4*3 = 12
        gen = Graph(n=4, m=12, directed=True)
        result = gen.generate(rng)
        assert len(result.edges) == 12

    def test_directed_exceeds_max_edges_raises(self):
        # n=4, directed max = 12, requesting 13
        with pytest.raises(ConstraintError) as exc_info:
            gen = Graph(n=4, m=13, directed=True)
            gen.generate(Random(42))
        assert "maximum" in str(exc_info.value)

    def test_self_loops_when_allowed(self, rng):
        gen = Graph(n=3, m=20, allow_self_loops=True, allow_multi_edges=True)
        found_self_loop = False
        for _ in range(10):
            result = gen.generate(rng)
            for u, v in result.edges:
                if u == v:
                    found_self_loop = True
                    break
            if found_self_loop:
                break
        assert found_self_loop

    def test_self_loops_increase_max(self, rng):
        # n=4, undirected with self loops: 4*3/2 + 4 = 10
        gen = Graph(n=4, m=10, allow_self_loops=True)
        result = gen.generate(rng)
        assert len(result.edges) == 10

    def test_multi_edges_allowed(self, rng):
        gen = Graph(n=2, m=10, allow_multi_edges=True)
        result = gen.generate(rng)
        assert len(result.edges) == 10  # Can have many edges between 2 nodes

    def test_generate_with_node_values(self, rng):
        gen = Graph(n=3, m=2, node_value=Int(1, 10))
        result = gen.generate(rng)
        assert result.node_values is not None
        assert len(result.node_values) == 4  # index 0 unused + 3 nodes
        for i in range(1, 4):
            assert 1 <= result.node_values[i] <= 10

    def test_generate_n_from_generator(self, rng):
        gen = Graph(n=Int(3, 5), m=2)
        for _ in range(10):
            result = gen.generate(rng)
            assert 3 <= result.n <= 5

    def test_generate_m_from_generator(self, rng):
        gen = Graph(n=5, m=Int(1, 3))
        for _ in range(10):
            result = gen.generate(rng)
            assert 1 <= result.m <= 3

    def test_validate_n_less_than_1_raises(self):
        with pytest.raises(ConstraintError) as exc_info:
            Graph(n=0, m=0)
        assert "n" in str(exc_info.value)

    def test_validate_m_negative_raises(self):
        with pytest.raises(ConstraintError) as exc_info:
            Graph(n=5, m=-1)
        assert "m" in str(exc_info.value)
        assert "negative" in str(exc_info.value)

    def test_validate_node_value_not_generator_raises(self):
        with pytest.raises(ConstraintError) as exc_info:
            Graph(n=5, m=5, node_value=42)
        assert "node_value" in str(exc_info.value)

    def test_generate_n_invalid_raises(self, rng):
        gen = Graph(n=Int(-5, 0), m=0)
        with pytest.raises(ConstraintError) as exc_info:
            gen.generate(rng)
        assert "generated n" in str(exc_info.value)

    def test_generate_m_invalid_raises(self, rng):
        gen = Graph(n=5, m=Int(-5, -1))
        with pytest.raises(ConstraintError) as exc_info:
            gen.generate(rng)
        assert "generated m" in str(exc_info.value)

    def test_repr_basic(self):
        gen = Graph(n=5, m=7)
        r = repr(gen)
        assert "Graph" in r
        assert "n=5" in r
        assert "m=7" in r

    def test_repr_with_options(self):
        gen = Graph(n=5, m=7, directed=True, allow_self_loops=True)
        r = repr(gen)
        assert "directed=True" in r
        assert "allow_self_loops=True" in r
