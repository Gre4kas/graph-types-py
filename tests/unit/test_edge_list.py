"""
Unit tests for EdgeListRepresentation.
"""

from __future__ import annotations

import pytest

from packages.core.edge import Edge
from packages.core.vertex import Vertex
from packages.representations.edge_list import EdgeListRepresentation


class TestEdgeListBasics:
    """Test basic EdgeList operations."""

    @pytest.fixture
    def empty_repr(self) -> EdgeListRepresentation:
        """Create empty edge list representation."""
        return EdgeListRepresentation(directed=False)

    @pytest.fixture
    def sample_repr(self) -> EdgeListRepresentation:
        """Create sample edge list with data."""
        repr = EdgeListRepresentation(directed=False)
        repr.add_vertex(Vertex(id="A"))
        repr.add_vertex(Vertex(id="B"))
        repr.add_vertex(Vertex(id="C"))
        repr.add_edge(Edge(source="A", target="B", weight=5.0))
        repr.add_edge(Edge(source="B", target="C", weight=3.0))
        return repr

    def test_create_empty(self, empty_repr: EdgeListRepresentation) -> None:
        """Test creating empty representation."""
        assert empty_repr.vertex_count() == 0
        assert empty_repr.edge_count() == 0

    def test_add_vertex(self, empty_repr: EdgeListRepresentation) -> None:
        """Test adding vertices."""
        vertex = Vertex(id="A", attributes={"color": "red"})
        empty_repr.add_vertex(vertex)
        
        assert empty_repr.vertex_count() == 1
        assert empty_repr.has_vertex("A")

    def test_add_duplicate_vertex_raises(
        self, 
        empty_repr: EdgeListRepresentation,
    ) -> None:
        """Test that adding duplicate vertex raises error."""
        empty_repr.add_vertex(Vertex(id="A"))
        
        with pytest.raises(ValueError, match="already exists"):
            empty_repr.add_vertex(Vertex(id="A"))

    def test_add_edge(self, sample_repr: EdgeListRepresentation) -> None:
        """Test adding edges."""
        assert sample_repr.edge_count() == 2
        assert sample_repr.has_edge("A", "B")
        assert sample_repr.has_edge("B", "C")

    def test_add_edge_nonexistent_vertex_raises(
        self,
        empty_repr: EdgeListRepresentation,
    ) -> None:
        """Test adding edge with nonexistent vertex raises error."""
        empty_repr.add_vertex(Vertex(id="A"))
        
        with pytest.raises(KeyError, match="not found"):
            empty_repr.add_edge(Edge(source="A", target="Z", weight=1.0))

    def test_has_edge_undirected(
        self,
        sample_repr: EdgeListRepresentation,
    ) -> None:
        """Test edge existence check for undirected graph."""
        # Undirected: both directions should work
        assert sample_repr.has_edge("A", "B")
        assert sample_repr.has_edge("B", "A")

    def test_get_neighbors(self, sample_repr: EdgeListRepresentation) -> None:
        """Test getting neighbors."""
        neighbors_a = sample_repr.get_neighbors("A")
        neighbors_b = sample_repr.get_neighbors("B")
        
        assert neighbors_a == {"B"}
        assert neighbors_b == {"A", "C"}

    def test_remove_vertex(self, sample_repr: EdgeListRepresentation) -> None:
        """Test removing vertex."""
        initial_edges = sample_repr.edge_count()
        
        sample_repr.remove_vertex("B")
        
        assert not sample_repr.has_vertex("B")
        assert sample_repr.vertex_count() == 2
        assert sample_repr.edge_count() < initial_edges

    def test_remove_edge(self, sample_repr: EdgeListRepresentation) -> None:
        """Test removing edge."""
        sample_repr.remove_edge("A", "B")
        
        assert not sample_repr.has_edge("A", "B")
        assert sample_repr.edge_count() == 1

    def test_to_list(self, sample_repr: EdgeListRepresentation) -> None:
        """Test exporting to list format."""
        edge_list = sample_repr.to_list()
        
        assert len(edge_list) == 2
        assert all(len(edge) == 3 for edge in edge_list)
        assert ("A", "B", 5.0) in edge_list or ("B", "A", 5.0) in edge_list


class TestEdgeListDirected:
    """Test EdgeList with directed graphs."""

    @pytest.fixture
    def directed_repr(self) -> EdgeListRepresentation:
        """Create directed edge list."""
        repr = EdgeListRepresentation(directed=True)
        repr.add_vertex(Vertex(id="A"))
        repr.add_vertex(Vertex(id="B"))
        repr.add_edge(Edge(source="A", target="B", weight=5.0, directed=True))
        return repr

    def test_has_edge_directed(
        self,
        directed_repr: EdgeListRepresentation,
    ) -> None:
        """Test edge check respects direction."""
        assert directed_repr.has_edge("A", "B")
        assert not directed_repr.has_edge("B", "A")

    def test_get_neighbors_directed(
        self,
        directed_repr: EdgeListRepresentation,
    ) -> None:
        """Test neighbors in directed graph."""
        assert directed_repr.get_neighbors("A") == {"B"}
        assert directed_repr.get_neighbors("B") == set()


class TestEdgeListPerformance:
    """Test EdgeList performance characteristics."""

    def test_large_edge_list(self) -> None:
        """Test with larger graph without violating uniqueness constraints."""
        repr = EdgeListRepresentation()

        # Add 100 vertices
        for i in range(100):
            repr.add_vertex(Vertex(id=i))

        # Add up to 100 unique edges (simple chain)
        edge_count = 0
        for i in range(99):
            repr.add_edge(Edge(source=i, target=i + 1, weight=float(i)))
            edge_count += 1

        #  Check basic invariants
        assert repr.vertex_count() == 100
        assert repr.edge_count() == edge_count

        # Sanity-checks
        assert repr.has_edge(0, 1)
        assert repr.has_edge(1, 2)
        assert not repr.has_edge(50, 10)

        # Check that duplicate is not allowed (class contract)
        with pytest.raises(ValueError):
            repr.add_edge(Edge(source=0, target=1, weight=123.0))

