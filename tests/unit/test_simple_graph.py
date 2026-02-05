"""
Unit tests for SimpleGraph.
"""

from __future__ import annotations

import pytest

from packages.graphs.simple_graph import SimpleGraph
from packages.utils.exceptions import GraphConstraintError, VertexNotFoundError


class TestSimpleGraphBasics:
    """Test basic SimpleGraph operations."""

    def test_create_empty_graph(self, empty_simple_graph: SimpleGraph) -> None:
        """Test creating empty graph."""
        assert empty_simple_graph.vertex_count() == 0
        assert empty_simple_graph.edge_count() == 0

    def test_add_vertex(self, empty_simple_graph: SimpleGraph) -> None:
        """Test adding vertices."""
        graph = empty_simple_graph
        graph.add_vertex("A", color="red")
        
        assert graph.vertex_count() == 1
        assert graph.has_vertex("A")

    def test_add_duplicate_vertex_raises(self, empty_simple_graph: SimpleGraph) -> None:
        """Test that adding duplicate vertex raises error."""
        graph = empty_simple_graph
        graph.add_vertex("A")
        
        with pytest.raises(ValueError, match="already exists"):
            graph.add_vertex("A")

    def test_add_edge(self, sample_simple_graph: SimpleGraph) -> None:
        """Test adding edges."""
        graph = sample_simple_graph
        
        assert graph.has_edge("A", "B")
        assert graph.has_edge("B", "C")
        assert graph.edge_count() == 2

    def test_add_self_loop_raises(self, empty_simple_graph: SimpleGraph) -> None:
        """Test that self-loops are rejected in simple graphs."""
        graph = empty_simple_graph
        graph.add_vertex("A")
        
        with pytest.raises(GraphConstraintError, match="self-loop"):
            graph.add_edge("A", "A")

    def test_remove_vertex(self, sample_simple_graph: SimpleGraph) -> None:
        """Test removing vertex."""
        graph = sample_simple_graph
        initial_edges = graph.edge_count()
        
        graph.remove_vertex("B")
        
        assert not graph.has_vertex("B")
        assert graph.vertex_count() == 2
        assert graph.edge_count() < initial_edges  # Edges removed

    def test_remove_nonexistent_vertex_raises(
        self,
        empty_simple_graph: SimpleGraph,
    ) -> None:
        """Test removing nonexistent vertex raises error."""
        with pytest.raises(VertexNotFoundError):
            empty_simple_graph.remove_vertex("Z")

    def test_get_neighbors(self, sample_simple_graph: SimpleGraph) -> None:
        """Test getting neighbors."""
        graph = sample_simple_graph
        neighbors = graph.get_neighbors("B")
        
        assert "A" in neighbors
        assert "C" in neighbors
        assert len(neighbors) == 2

    def test_degree(self, sample_simple_graph: SimpleGraph) -> None:
        """Test vertex degree calculation."""
        graph = sample_simple_graph
        
        assert graph.degree("A") == 1
        assert graph.degree("B") == 2
        assert graph.degree("C") == 1


class TestSimpleGraphRepresentations:
    """Test representation conversions."""

    def test_convert_to_adjacency_matrix(
        self,
        sample_simple_graph: SimpleGraph,
    ) -> None:
        """Test converting to adjacency matrix representation."""
        graph = sample_simple_graph
        initial_edges = list(graph.edges())
        
        graph.convert_representation("adjacency_matrix")
        
        # Verify structure preserved
        assert graph.vertex_count() == 3
        assert graph.edge_count() == len(initial_edges)
        assert graph.has_edge("A", "B")

    def test_convert_back_to_list(self, sample_simple_graph: SimpleGraph) -> None:
        """Test converting back to adjacency list."""
        graph = sample_simple_graph
        
        graph.convert_representation("adjacency_matrix")
        graph.convert_representation("adjacency_list")
        
        assert graph.has_edge("A", "B")
        assert graph.has_edge("B", "C")


class TestSimpleGraphConversions:
    """Test graph type conversions."""

    def test_to_multigraph(self, sample_simple_graph: SimpleGraph) -> None:
        """Test converting to multigraph."""
        simple = sample_simple_graph
        multi = simple.to_multigraph()
        
        assert multi.vertex_count() == simple.vertex_count()
        assert multi.edge_count() == simple.edge_count()
        
        # Now can add parallel edges
        multi.add_edge("A", "B", weight=10.0)
        assert multi.edge_count() > simple.edge_count()

    def test_to_pseudograph(self, sample_simple_graph: SimpleGraph) -> None:
        """Test converting to pseudograph."""
        simple = sample_simple_graph
        pseudo = simple.to_pseudograph()
        
        assert pseudo.vertex_count() == simple.vertex_count()
        
        # Now can add self-loops
        pseudo.add_edge("A", "A", weight=1.0)
        assert pseudo.has_self_loop("A")
