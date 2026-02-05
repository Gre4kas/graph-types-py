"""
Unit tests for graph algorithms.
"""

from __future__ import annotations

import pytest

from packages.algorithms.shortest_path import dijkstra, reconstruct_path
from packages.algorithms.traversal import bfs, dfs, has_path, is_connected
from packages.graphs.simple_graph import SimpleGraph


class TestTraversal:
    """Test graph traversal algorithms."""

    @pytest.fixture
    def linear_graph(self) -> SimpleGraph:
        """Create linear graph A-B-C-D."""
        graph = SimpleGraph()
        for v in ["A", "B", "C", "D"]:
            graph.add_vertex(v)
        graph.add_edge("A", "B")
        graph.add_edge("B", "C")
        graph.add_edge("C", "D")
        return graph

    def test_bfs_order(self, linear_graph: SimpleGraph) -> None:
        """Test BFS returns correct order."""
        result = list(bfs(linear_graph, "A"))
        assert result == ["A", "B", "C", "D"]

    def test_bfs_with_depth(self, linear_graph: SimpleGraph) -> None:
        """Test BFS with depth information."""
        result = list(bfs(linear_graph, "A", yield_depth=True))
        
        assert result[0] == ("A", 0)
        assert result[1] == ("B", 1)
        assert result[2] == ("C", 2)
        assert result[3] == ("D", 3)

    def test_dfs_visits_all(self, linear_graph: SimpleGraph) -> None:
        """Test DFS visits all vertices."""
        result = list(dfs(linear_graph, "A"))
        assert len(result) == 4
        assert set(result) == {"A", "B", "C", "D"}

    def test_dfs_recursive(self, linear_graph: SimpleGraph) -> None:
        """Test recursive DFS."""
        result = list(dfs(linear_graph, "A", recursive=True))
        assert len(result) == 4

    def test_has_path_true(self, linear_graph: SimpleGraph) -> None:
        """Test path existence detection."""
        assert has_path(linear_graph, "A", "D")

    def test_has_path_false(self) -> None:
        """Test path non-existence detection."""
        graph = SimpleGraph()
        graph.add_vertex("A")
        graph.add_vertex("B")
        
        assert not has_path(graph, "A", "B")

    def test_is_connected_true(self, linear_graph: SimpleGraph) -> None:
        """Test connected graph detection."""
        assert is_connected(linear_graph)

    def test_is_connected_false(self) -> None:
        """Test disconnected graph detection."""
        graph = SimpleGraph()
        graph.add_vertex("A")
        graph.add_vertex("B")
        graph.add_vertex("C")
        graph.add_edge("A", "B")
        
        assert not is_connected(graph)


class TestShortestPath:
    """Test shortest path algorithms."""

    @pytest.fixture
    def weighted_graph(self) -> SimpleGraph:
        """Create weighted graph for shortest path tests."""
        graph = SimpleGraph()
        for v in ["A", "B", "C", "D"]:
            graph.add_vertex(v)
        
        graph.add_edge("A", "B", weight=4.0)
        graph.add_edge("A", "C", weight=2.0)
        graph.add_edge("B", "C", weight=1.0)
        graph.add_edge("B", "D", weight=5.0)
        graph.add_edge("C", "D", weight=8.0)
        
        return graph

    def test_dijkstra_distances(self, weighted_graph: SimpleGraph) -> None:
        """Test Dijkstra computes correct distances."""
        distances = dijkstra(weighted_graph, "A")
        
        assert distances["A"] == 0.0
        assert distances["B"] == 4.0
        assert distances["C"] == 2.0
        assert distances["D"] == 9.0

    def test_dijkstra_with_target(self, weighted_graph: SimpleGraph) -> None:
        """Test Dijkstra with target vertex."""
        distances, predecessors = dijkstra(weighted_graph, "A", "D")
        
        assert distances["D"] == 9.0
        
        path = reconstruct_path(predecessors, "A", "D")
        assert path is not None
        assert path[0] == "A"
        assert path[-1] == "D"

    def test_reconstruct_path(self, weighted_graph: SimpleGraph) -> None:
        """Test path reconstruction."""
        _, predecessors = dijkstra(weighted_graph, "A", "D")
        path = reconstruct_path(predecessors, "A", "D")
        
        assert path is not None
        assert len(path) >= 2
        assert path[0] == "A"
        assert path[-1] == "D"
