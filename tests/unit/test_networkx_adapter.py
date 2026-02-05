"""
Unit tests for NetworkX integration.
"""

from __future__ import annotations

import pytest

from packages.graphs.simple_graph import SimpleGraph
from packages.integrations.networkx_adapter import (
    NETWORKX_AVAILABLE,
    NetworkXAdapter,
    NetworkXAlgorithms,
)

# Skip all tests if NetworkX not installed
pytestmark = pytest.mark.skipif(
    not NETWORKX_AVAILABLE,
    reason="NetworkX not installed",
)


class TestNetworkXAdapter:
    """Test NetworkX adapter conversions."""

    @pytest.fixture
    def sample_graph(self) -> SimpleGraph:
        """Create sample graph."""
        graph = SimpleGraph()
        graph.add_vertex("A", color="red", size=10)
        graph.add_vertex("B", color="blue", size=20)
        graph.add_vertex("C", color="green", size=15)
        graph.add_edge("A", "B", weight=5.0, label="edge1")
        graph.add_edge("B", "C", weight=3.0, label="edge2")
        graph.add_edge("A", "C", weight=10.0, label="edge3")
        return graph

    def test_to_networkx(self, sample_graph: SimpleGraph) -> None:
        """Test converting our graph to NetworkX."""
        nx_graph = NetworkXAdapter.to_networkx(sample_graph)

        assert nx_graph.number_of_nodes() == 3
        assert nx_graph.number_of_edges() == 3
        assert nx_graph.has_node("A")
        assert nx_graph.has_edge("A", "B")

    def test_to_networkx_preserves_vertex_attributes(
        self,
        sample_graph: SimpleGraph,
    ) -> None:
        """Test that vertex attributes are preserved."""
        nx_graph = NetworkXAdapter.to_networkx(sample_graph)

        node_a = nx_graph.nodes["A"]
        assert node_a["color"] == "red"
        assert node_a["size"] == 10

    def test_to_networkx_preserves_edge_attributes(
        self,
        sample_graph: SimpleGraph,
    ) -> None:
        """Test that edge attributes are preserved."""
        nx_graph = NetworkXAdapter.to_networkx(sample_graph)

        edge_ab = nx_graph.edges["A", "B"]
        assert edge_ab["weight"] == 5.0
        assert edge_ab["label"] == "edge1"

    def test_to_networkx_directed(self) -> None:
        """Test converting directed graph."""
        graph = SimpleGraph(directed=True)
        graph.add_vertex("X")
        graph.add_vertex("Y")
        graph.add_edge("X", "Y", weight=1.0)

        nx_graph = NetworkXAdapter.to_networkx(graph)

        assert nx_graph.is_directed()
        assert nx_graph.has_edge("X", "Y")
        assert not nx_graph.has_edge("Y", "X")

    def test_from_networkx(self) -> None:
        """Test converting NetworkX graph to ours."""
        import networkx as nx

        # Create NetworkX graph
        nx_graph = nx.Graph()
        nx_graph.add_node("A", priority=1)
        nx_graph.add_node("B", priority=2)
        nx_graph.add_edge("A", "B", weight=5.0, type="strong")

        # Convert to our graph
        graph = NetworkXAdapter.from_networkx(nx_graph)

        assert graph.vertex_count() == 2
        assert graph.edge_count() == 1
        assert graph.has_vertex("A")
        assert graph.has_edge("A", "B")

    def test_from_networkx_preserves_attributes(self) -> None:
        """Test that attributes are preserved when converting from NetworkX."""
        import networkx as nx

        nx_graph = nx.Graph()
        nx_graph.add_node("A", value=100, tag="important")
        nx_graph.add_node("B", value=200, tag="normal")
        nx_graph.add_edge("A", "B", weight=5.0, relation="parent")

        graph = NetworkXAdapter.from_networkx(nx_graph)

        vertex_a = graph.get_vertex("A")
        assert vertex_a.attributes["value"] == 100
        assert vertex_a.attributes["tag"] == "important"

        edge_ab = graph.get_edge("A", "B")
        assert edge_ab.weight == 5.0
        assert edge_ab.attributes["relation"] == "parent"

    def test_roundtrip_conversion(self, sample_graph: SimpleGraph) -> None:
        """Test that our_graph -> NetworkX -> our_graph preserves structure."""
        # Convert to NetworkX and back
        nx_graph = NetworkXAdapter.to_networkx(sample_graph)
        restored = NetworkXAdapter.from_networkx(nx_graph)

        # Check structure preserved
        assert restored.vertex_count() == sample_graph.vertex_count()
        assert restored.edge_count() == sample_graph.edge_count()

        # Check vertices
        original_vertices = {v.id for v in sample_graph.vertices()}
        restored_vertices = {v.id for v in restored.vertices()}
        assert original_vertices == restored_vertices

    def test_karate_club_graph(self) -> None:
        """Test with NetworkX's famous karate club graph."""
        import networkx as nx

        # Load Zachary's Karate Club graph
        nx_karate = nx.karate_club_graph()

        # Convert to our graph
        graph = NetworkXAdapter.from_networkx(nx_karate)

        assert graph.vertex_count() == 34
        assert graph.edge_count() == 78
        assert not graph._directed


class TestNetworkXAlgorithms:
    """Test NetworkX algorithm wrappers."""

    @pytest.fixture
    def sample_graph(self) -> SimpleGraph:
        """Create sample graph for testing algorithms."""
        graph = SimpleGraph()
        for i in range(5):
            graph.add_vertex(i)

        # Create a connected graph
        edges = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 0), (1, 3)]
        for source, target in edges:
            graph.add_edge(source, target, weight=1.0)

        return graph

    def test_betweenness_centrality(self, sample_graph: SimpleGraph) -> None:
        """Test betweenness centrality calculation."""
        centrality = NetworkXAlgorithms.betweenness_centrality(sample_graph)

        assert isinstance(centrality, dict)
        assert len(centrality) == 5
        assert all(0 <= v <= 1 for v in centrality.values())

    def test_closeness_centrality(self, sample_graph: SimpleGraph) -> None:
        """Test closeness centrality calculation."""
        centrality = NetworkXAlgorithms.closeness_centrality(sample_graph)

        assert isinstance(centrality, dict)
        assert len(centrality) == 5
        assert all(0 <= v <= 1 for v in centrality.values())

    def test_pagerank(self, sample_graph: SimpleGraph) -> None:
        """Test PageRank calculation."""
        pagerank = NetworkXAlgorithms.pagerank(sample_graph)

        assert isinstance(pagerank, dict)
        assert len(pagerank) == 5
        # PageRank values sum to ~1.0
        assert 0.99 <= sum(pagerank.values()) <= 1.01

    def test_detect_communities(self, sample_graph: SimpleGraph) -> None:
        """Test community detection."""
        communities = NetworkXAlgorithms.detect_communities(sample_graph)

        assert isinstance(communities, list)
        assert len(communities) >= 1
        assert all(isinstance(c, set) for c in communities)

        # All vertices should be in some community
        all_vertices = set()
        for community in communities:
            all_vertices.update(community)
        assert len(all_vertices) == 5

    def test_is_connected(self, sample_graph: SimpleGraph) -> None:
        """Test connectivity check."""
        is_connected = NetworkXAlgorithms.is_connected(sample_graph)
        assert is_connected is True

        # Test with disconnected graph
        disconnected = SimpleGraph()
        disconnected.add_vertex("A")
        disconnected.add_vertex("B")
        disconnected.add_vertex("C")
        disconnected.add_edge("A", "B")
        # C is isolated

        is_connected = NetworkXAlgorithms.is_connected(disconnected)
        assert is_connected is False

    def test_clustering_coefficient(self, sample_graph: SimpleGraph) -> None:
        """Test clustering coefficient calculation."""
        clustering = NetworkXAlgorithms.clustering_coefficient(sample_graph)

        assert isinstance(clustering, dict)
        assert len(clustering) == 5
        assert all(0 <= v <= 1 for v in clustering.values())

    def test_minimum_spanning_tree(self) -> None:
        """Test MST calculation."""
        graph = SimpleGraph()
        graph.add_vertex("A")
        graph.add_vertex("B")
        graph.add_vertex("C")
        graph.add_vertex("D")

        graph.add_edge("A", "B", weight=1.0)
        graph.add_edge("B", "C", weight=2.0)
        graph.add_edge("C", "D", weight=1.0)
        graph.add_edge("A", "D", weight=5.0)

        mst = NetworkXAlgorithms.minimum_spanning_tree(graph)

        # MST of 4 vertices should have 3 edges
        assert mst.vertex_count() == 4
        assert mst.edge_count() == 3

    def test_all_pairs_shortest_path(self, sample_graph: SimpleGraph) -> None:
        """Test all pairs shortest path calculation."""
        paths = NetworkXAlgorithms.all_pairs_shortest_path(sample_graph)

        assert isinstance(paths, dict)
        assert len(paths) == 5

        # Check a specific path exists
        assert 0 in paths
        assert 2 in paths[0]
        assert isinstance(paths[0][2], list)


class TestNetworkXAvailability:
    """Test NetworkX availability handling."""

    def test_networkx_available_flag(self) -> None:
        """Test that NETWORKX_AVAILABLE flag is correct."""
        # This test runs only if NetworkX is installed
        assert NETWORKX_AVAILABLE is True

    def test_adapter_check(self) -> None:
        """Test that adapter doesn't raise when NetworkX available."""
        # Should not raise
        NetworkXAdapter._check_networkx_available()

    def test_algorithms_check(self) -> None:
        """Test that algorithms don't raise when NetworkX available."""
        # Should not raise
        NetworkXAlgorithms._check_networkx_available()


class TestComplexGraphs:
    """Test with more complex graph structures."""

    def test_complete_graph(self) -> None:
        """Test with complete graph."""
        import networkx as nx

        # Create complete graph K5
        nx_complete = nx.complete_graph(5)
        graph = NetworkXAdapter.from_networkx(nx_complete)

        assert graph.vertex_count() == 5
        assert graph.edge_count() == 10  # K5 has n(n-1)/2 = 10 edges

    def test_path_graph(self) -> None:
        """Test with path graph."""
        import networkx as nx

        # Create path graph P5
        nx_path = nx.path_graph(5)
        graph = NetworkXAdapter.from_networkx(nx_path)

        assert graph.vertex_count() == 5
        assert graph.edge_count() == 4  # Path has n-1 edges

    def test_cycle_graph(self) -> None:
        """Test with cycle graph."""
        import networkx as nx

        # Create cycle graph C5
        nx_cycle = nx.cycle_graph(5)
        graph = NetworkXAdapter.from_networkx(nx_cycle)

        assert graph.vertex_count() == 5
        assert graph.edge_count() == 5  # Cycle has n edges

    def test_star_graph(self) -> None:
        """Test with star graph."""
        import networkx as nx

        # Create star graph S5 (center + 5 leaves)
        nx_star = nx.star_graph(5)
        graph = NetworkXAdapter.from_networkx(nx_star)

        assert graph.vertex_count() == 6
        assert graph.edge_count() == 5  # Star has n edges
