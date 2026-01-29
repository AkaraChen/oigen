"""
Tests for oigen.generators.tree module.
"""

from random import Random

import pytest

from oigen.errors import ConstraintError
from oigen.generators import Int
from oigen.generators.tree import Tree, TreeData


class TestTreeData:
    def test_str_format_basic(self):
        data = TreeData(n=3, edges=[(1, 2), (1, 3)])
        s = str(data)
        lines = s.strip().split("\n")
        assert lines[0] == "3"  # n
        assert len(lines) == 3  # n + 2 edges

    def test_str_format_with_node_values(self):
        data = TreeData(n=3, edges=[(1, 2), (1, 3)], node_values=[None, 10, 20, 30])
        s = str(data)
        lines = s.strip().split("\n")
        assert lines[0] == "3"  # n
        assert lines[1] == "10 20 30"  # node values
        assert len(lines) == 4  # n + values + 2 edges

    def test_str_format_single_node(self):
        data = TreeData(n=1, edges=[])
        s = str(data)
        assert s.strip() == "1"

    def test_str_format_edge_order(self):
        data = TreeData(n=3, edges=[(2, 3), (1, 2)])
        s = str(data)
        lines = s.strip().split("\n")
        assert "2 3" in lines[1] or "2 3" in lines[2]
        assert "1 2" in lines[1] or "1 2" in lines[2]


class TestTree:
    def test_generate_correct_edge_count(self, rng):
        gen = Tree(n=5)
        result = gen.generate(rng)
        assert result.n == 5
        assert len(result.edges) == 4  # n-1 edges

    def test_generate_single_node(self, rng):
        gen = Tree(n=1)
        result = gen.generate(rng)
        assert result.n == 1
        assert len(result.edges) == 0

    def test_generate_two_nodes(self, rng):
        gen = Tree(n=2)
        result = gen.generate(rng)
        assert result.n == 2
        assert len(result.edges) == 1

    def test_generate_deterministic(self):
        gen = Tree(n=10)
        rng1 = Random(42)
        rng2 = Random(42)
        result1 = gen.generate(rng1)
        result2 = gen.generate(rng2)
        assert result1.n == result2.n
        assert result1.edges == result2.edges

    def test_generate_valid_edges(self, rng):
        gen = Tree(n=5)
        result = gen.generate(rng)
        for u, v in result.edges:
            assert 1 <= u <= 5
            assert 1 <= v <= 5
            assert u != v

    def test_generate_connected_tree(self, rng):
        gen = Tree(n=10)
        result = gen.generate(rng)

        # Build adjacency list and verify connectivity
        adj = {i: [] for i in range(1, 11)}
        for u, v in result.edges:
            adj[u].append(v)
            adj[v].append(u)

        # BFS from node 1
        visited = set()
        queue = [1]
        while queue:
            node = queue.pop(0)
            if node in visited:
                continue
            visited.add(node)
            queue.extend(adj[node])

        assert len(visited) == 10  # All nodes reachable

    def test_generate_with_node_values(self, rng):
        gen = Tree(n=3, node_value=Int(1, 10))
        result = gen.generate(rng)
        assert result.node_values is not None
        assert len(result.node_values) == 4  # index 0 unused + 3 nodes
        for i in range(1, 4):
            assert 1 <= result.node_values[i] <= 10

    def test_generate_without_node_values(self, rng):
        gen = Tree(n=3)
        result = gen.generate(rng)
        assert result.node_values is None

    def test_generate_n_from_generator(self, rng):
        gen = Tree(n=Int(5, 10))
        for _ in range(10):
            result = gen.generate(rng)
            assert 5 <= result.n <= 10
            assert len(result.edges) == result.n - 1

    def test_validate_n_less_than_1_raises(self):
        with pytest.raises(ConstraintError) as exc_info:
            Tree(n=0)
        assert "n" in str(exc_info.value)
        assert ">= 1" in str(exc_info.value)

    def test_validate_node_value_not_generator_raises(self):
        with pytest.raises(ConstraintError) as exc_info:
            Tree(n=5, node_value=42)
        assert "node_value" in str(exc_info.value)
        assert "generator" in str(exc_info.value)

    def test_generate_n_from_generator_invalid_raises(self, rng):
        gen = Tree(n=Int(-5, 0))
        with pytest.raises(ConstraintError) as exc_info:
            gen.generate(rng)
        assert "generated n" in str(exc_info.value)

    def test_repr_basic(self):
        gen = Tree(n=5)
        assert "Tree" in repr(gen)
        assert "5" in repr(gen)

    def test_repr_with_node_value(self):
        gen = Tree(n=5, node_value=Int(1, 10))
        r = repr(gen)
        assert "Tree" in r
        assert "node_value" in r
