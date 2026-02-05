"""
Pytest fixtures for graph library tests.
"""

from __future__ import annotations

import pytest

from packages.graphs.hypergraph import Hypergraph
from packages.graphs.multigraph import Multigraph
from packages.graphs.pseudograph import Pseudograph
from packages.graphs.simple_graph import SimpleGraph


@pytest.fixture
def empty_simple_graph() -> SimpleGraph:
    """Create empty simple graph."""
    return SimpleGraph()


@pytest.fixture
def sample_simple_graph() -> SimpleGraph:
    """Create sample simple graph with vertices and edges."""
    graph = SimpleGraph()
    graph.add_vertex("A", color="red")
    graph.add_vertex("B", color="blue")
    graph.add_vertex("C", color="green")
    graph.add_edge("A", "B", weight=5.0)
    graph.add_edge("B", "C", weight=3.0)
    return graph


@pytest.fixture
def sample_multigraph() -> Multigraph:
    """Create sample multigraph with parallel edges."""
    graph = Multigraph()
    graph.add_vertex("A")
    graph.add_vertex("B")
    graph.add_edge("A", "B", weight=3.0)
    graph.add_edge("A", "B", weight=5.0)
    return graph


@pytest.fixture
def sample_pseudograph() -> Pseudograph:
    """Create sample pseudograph with self-loops."""
    graph = Pseudograph()
    graph.add_vertex("A")
    graph.add_vertex("B")
    graph.add_edge("A", "A", weight=1.0)
    graph.add_edge("A", "B", weight=2.0)
    return graph


@pytest.fixture
def sample_hypergraph() -> Hypergraph:
    """Create sample hypergraph."""
    graph = Hypergraph()
    for v in ["A", "B", "C", "D"]:
        graph.add_vertex(v)
    graph.add_hyperedge({"A", "B"}, weight=1.0)
    graph.add_hyperedge({"B", "C", "D"}, weight=2.0)
    return graph
