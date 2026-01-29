"""
Shared pytest fixtures for oigen tests.
"""

from random import Random

import pytest


@pytest.fixture
def seeded_random() -> Random:
    """Provide a seeded Random instance for deterministic tests."""
    return Random(42)


@pytest.fixture
def rng() -> Random:
    """Alias for seeded_random fixture."""
    return Random(42)
