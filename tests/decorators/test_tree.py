"""
Tests for oigen.decorators.tree module.
"""

import pytest

from oigen.errors import ConstraintError
from oigen.generators import Int
from oigen.generators.tree import Tree
from oigen.decorators.base import get_constraints
from oigen.decorators.tree import (
    NodeWeightConstraint,
    EdgeWeightConstraint,
    DiameterConstraint,
    CentroidConstraint,
    DepthConstraint,
    with_node_weight,
    with_edge_weight,
    with_diameter,
    with_centroid,
    with_depth,
)


class TestNodeWeightConstraint:
    def test_validate_valid(self):
        c = NodeWeightConstraint(generator=Int(1, 10))
        c.validate(Tree(n=5), get_constraints(lambda: Tree(n=5)) or __import__('oigen.decorators.base', fromlist=['ConstraintRegistry']).ConstraintRegistry())

    def test_validate_invalid_generator(self):
        c = NodeWeightConstraint(generator=42)  # type: ignore
        from oigen.decorators.base import ConstraintRegistry
        with pytest.raises(ConstraintError) as exc_info:
            c.validate(Tree(n=5), ConstraintRegistry())
        assert "generator must be a BaseGenerator" in str(exc_info.value)

    def test_apply(self):
        c = NodeWeightConstraint(generator=Int(1, 10))
        context = {}
        c.apply(Tree(n=5), context)
        assert "node_weight" in context

    def test_priority(self):
        c = NodeWeightConstraint(generator=Int(1, 10))
        assert c.priority == 50


class TestEdgeWeightConstraint:
    def test_validate_valid(self):
        c = EdgeWeightConstraint(generator=Int(1, 10))
        from oigen.decorators.base import ConstraintRegistry
        c.validate(Tree(n=5), ConstraintRegistry())

    def test_validate_invalid_generator(self):
        c = EdgeWeightConstraint(generator="not a gen")  # type: ignore
        from oigen.decorators.base import ConstraintRegistry
        with pytest.raises(ConstraintError) as exc_info:
            c.validate(Tree(n=5), ConstraintRegistry())
        assert "generator must be a BaseGenerator" in str(exc_info.value)

    def test_apply(self):
        c = EdgeWeightConstraint(generator=Int(1, 10))
        context = {}
        c.apply(Tree(n=5), context)
        assert "edge_weight" in context


class TestDiameterConstraint:
    def test_validate_valid(self):
        c = DiameterConstraint(min_val=3, max_val=5)
        from oigen.decorators.base import ConstraintRegistry
        c.validate(Tree(n=10), ConstraintRegistry())

    def test_validate_min_less_than_1(self):
        c = DiameterConstraint(min_val=0, max_val=5)
        from oigen.decorators.base import ConstraintRegistry
        with pytest.raises(ConstraintError) as exc_info:
            c.validate(Tree(n=10), ConstraintRegistry())
        assert "min" in str(exc_info.value) and ">= 1" in str(exc_info.value)

    def test_validate_min_greater_than_max(self):
        c = DiameterConstraint(min_val=5, max_val=3)
        from oigen.decorators.base import ConstraintRegistry
        with pytest.raises(ConstraintError) as exc_info:
            c.validate(Tree(n=10), ConstraintRegistry())
        assert "min" in str(exc_info.value) and "max" in str(exc_info.value)

    def test_validate_min_exceeds_n(self):
        c = DiameterConstraint(min_val=10, max_val=15)
        from oigen.decorators.base import ConstraintRegistry
        with pytest.raises(ConstraintError) as exc_info:
            c.validate(Tree(n=5), ConstraintRegistry())  # n-1 = 4, but min is 10
        assert "n-1" in str(exc_info.value)

    def test_apply(self):
        c = DiameterConstraint(min_val=3, max_val=5)
        context = {}
        c.apply(Tree(n=10), context)
        assert context["diameter"] == (3, 5)


class TestCentroidConstraint:
    def test_validate_valid_1(self):
        c = CentroidConstraint(count=1)
        from oigen.decorators.base import ConstraintRegistry
        c.validate(Tree(n=10), ConstraintRegistry())

    def test_validate_valid_2(self):
        c = CentroidConstraint(count=2)
        from oigen.decorators.base import ConstraintRegistry
        c.validate(Tree(n=10), ConstraintRegistry())

    def test_validate_invalid_count(self):
        c = CentroidConstraint(count=3)
        from oigen.decorators.base import ConstraintRegistry
        with pytest.raises(ConstraintError) as exc_info:
            c.validate(Tree(n=10), ConstraintRegistry())
        assert "1 or 2" in str(exc_info.value)

    def test_apply(self):
        c = CentroidConstraint(count=1)
        context = {}
        c.apply(Tree(n=10), context)
        assert context["centroid_count"] == 1


class TestDepthConstraint:
    def test_validate_valid(self):
        c = DepthConstraint(min_val=2, max_val=4)
        from oigen.decorators.base import ConstraintRegistry
        c.validate(Tree(n=10), ConstraintRegistry())

    def test_validate_min_less_than_1(self):
        c = DepthConstraint(min_val=0, max_val=5)
        from oigen.decorators.base import ConstraintRegistry
        with pytest.raises(ConstraintError) as exc_info:
            c.validate(Tree(n=10), ConstraintRegistry())
        assert "min" in str(exc_info.value)

    def test_validate_min_greater_than_max(self):
        c = DepthConstraint(min_val=5, max_val=2)
        from oigen.decorators.base import ConstraintRegistry
        with pytest.raises(ConstraintError) as exc_info:
            c.validate(Tree(n=10), ConstraintRegistry())
        assert "min" in str(exc_info.value) and "max" in str(exc_info.value)

    def test_validate_min_exceeds_n(self):
        c = DepthConstraint(min_val=10, max_val=15)
        from oigen.decorators.base import ConstraintRegistry
        with pytest.raises(ConstraintError) as exc_info:
            c.validate(Tree(n=5), ConstraintRegistry())
        assert "n-1" in str(exc_info.value)

    def test_validate_incompatible_with_diameter(self):
        c = DepthConstraint(min_val=1, max_val=2)
        from oigen.decorators.base import ConstraintRegistry
        registry = ConstraintRegistry()
        registry.add(DiameterConstraint(min_val=8, max_val=10))  # Requires depth >= 4
        with pytest.raises(ConstraintError) as exc_info:
            c.validate(Tree(n=20), registry)
        assert "diameter" in str(exc_info.value)

    def test_apply(self):
        c = DepthConstraint(min_val=2, max_val=4)
        context = {}
        c.apply(Tree(n=10), context)
        assert context["depth"] == (2, 4)


class TestDecoratorFunctions:
    def test_with_node_weight(self):
        @with_node_weight(Int(1, 100))
        def weighted():
            return Tree(n=5)

        registry = get_constraints(weighted)
        assert registry is not None
        assert registry.has(NodeWeightConstraint)

    def test_with_edge_weight(self):
        @with_edge_weight(Int(1, 100))
        def weighted():
            return Tree(n=5)

        registry = get_constraints(weighted)
        assert registry is not None
        assert registry.has(EdgeWeightConstraint)

    def test_with_diameter_range(self):
        @with_diameter(3, 5)
        def constrained():
            return Tree(n=10)

        registry = get_constraints(constrained)
        assert registry is not None
        c = registry.get_one(DiameterConstraint)
        assert c is not None
        assert c.min_val == 3
        assert c.max_val == 5

    def test_with_diameter_exact(self):
        @with_diameter(4)
        def constrained():
            return Tree(n=10)

        registry = get_constraints(constrained)
        c = registry.get_one(DiameterConstraint)
        assert c is not None
        assert c.min_val == 4
        assert c.max_val == 4

    def test_with_centroid(self):
        @with_centroid(1)
        def constrained():
            return Tree(n=10)

        registry = get_constraints(constrained)
        assert registry is not None
        assert registry.has(CentroidConstraint)

    def test_with_depth_range(self):
        @with_depth(2, 4)
        def constrained():
            return Tree(n=10)

        registry = get_constraints(constrained)
        c = registry.get_one(DepthConstraint)
        assert c is not None
        assert c.min_val == 2
        assert c.max_val == 4

    def test_with_depth_exact(self):
        @with_depth(3)
        def constrained():
            return Tree(n=10)

        registry = get_constraints(constrained)
        c = registry.get_one(DepthConstraint)
        assert c is not None
        assert c.min_val == 3
        assert c.max_val == 3
