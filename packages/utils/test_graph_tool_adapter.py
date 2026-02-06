"""
Unit tests for graph-tool integration.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from packages.graphs.simple_graph import SimpleGraph
from packages.integrations.graph_tool_adapter import (
    GRAPH_TOOL_AVAILABLE,
    GraphToolAdapter,
    GraphToolVisualizer,
)

# Skip all tests if graph-tool not installed
pytestmark = pytest.mark.skipif(
    not GRAPH_TOOL_AVAILABLE,
    reason="graph-tool not installed",
)


class TestGraphToolAdapter:
    """Test graph-tool adapter conversions."""

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

    def test_to_graph_tool(self, sample_graph: SimpleGraph) -> None:
        """Test converting our graph to graph-tool."""
        gt_graph = GraphToolAdapter.to_graph_tool(sample_graph)

        assert gt_graph.num_vertices() == 3
        assert gt_graph.num_edges() == 3
        assert not gt_graph.is_directed()

    def test_to_graph_tool_preserves_vertex_count(
        self,
        sample_graph: SimpleGraph,
    ) -> None:
        """Test that vertex count is preserved."""
        gt_graph = GraphToolAdapter.to_graph_tool(sample_graph)
        assert gt_graph.num_vertices() == sample_graph.vertex_count()

    def test_to_graph_tool_preserves_edge_count(
        self,
        sample_graph: SimpleGraph,
    ) -> None:
        """Test that edge count is preserved."""
        gt_graph = GraphToolAdapter.to_graph_tool(sample_graph)
        assert gt_graph.num_edges() == sample_graph.edge_count()

    def test_to_graph_tool_creates_original_id_property(
        self,
        sample_graph: SimpleGraph,
    ) -> None:
        """Test that original vertex IDs are stored."""
        gt_graph = GraphToolAdapter.to_graph_tool(sample_graph)

        assert "original_id" in gt_graph.vp
        
        # Check that all original IDs are present
        original_ids = [gt_graph.vp.original_id[v] for v in gt_graph.vertices()]
        assert set(original_ids) == {"A", "B", "C"}

    def test_to_graph_tool_preserves_vertex_attributes(
        self,
        sample_graph: SimpleGraph,
    ) -> None:
        """Test that vertex attributes are preserved."""
        gt_graph = GraphToolAdapter.to_graph_tool(sample_graph)

        # Check that attribute property maps exist
        assert "color" in gt_graph.vp
        assert "size" in gt_graph.vp

        # Check specific values
        for v in gt_graph.vertices():
            vid = gt_graph.vp.original_id[v]
            if vid == "A":
                assert gt_graph.vp.color[v] == "red"
                assert gt_graph.vp.size[v] == 10

    def test_to_graph_tool_preserves_edge_weights(
        self,
        sample_graph: SimpleGraph,
    ) -> None:
        """Test that edge weights are preserved."""
        gt_graph = GraphToolAdapter.to_graph_tool(sample_graph)

        assert "weight" in gt_graph.ep

        # Check that weights exist
        weights = [gt_graph.ep.weight[e] for e in gt_graph.edges()]
        assert len(weights) == 3
        assert all(w > 0 for w in weights)

    def test_to_graph_tool_preserves_edge_attributes(
        self,
        sample_graph: SimpleGraph,
    ) -> None:
        """Test that edge attributes are preserved."""
        gt_graph = GraphToolAdapter.to_graph_tool(sample_graph)

        assert "label" in gt_graph.ep

        # Check specific labels
        labels = [gt_graph.ep.label[e] for e in gt_graph.edges()]
        assert set(labels) == {"edge1", "edge2", "edge3"}

    def test_to_graph_tool_directed(self) -> None:
        """Test converting directed graph."""
        graph = SimpleGraph(directed=True)
        graph.add_vertex("X")
        graph.add_vertex("Y")
        graph.add_edge("X", "Y", weight=1.0)

        gt_graph = GraphToolAdapter.to_graph_tool(graph)

        assert gt_graph.is_directed()
        assert gt_graph.num_vertices() == 2
        assert gt_graph.num_edges() == 1

    def test_from_graph_tool(self) -> None:
        """Test converting graph-tool graph to ours."""
        import graph_tool.all as gt

        # Create graph-tool graph
        gt_graph = gt.Graph(directed=False)
        
        # Add vertices
        v1 = gt_graph.add_vertex()
        v2 = gt_graph.add_vertex()
        v3 = gt_graph.add_vertex()
        
        # Store original IDs
        original_id = gt_graph.new_vertex_property("string")
        original_id[v1] = "A"
        original_id[v2] = "B"
        original_id[v3] = "C"
        gt_graph.vp["original_id"] = original_id
        
        # Add edges with weights
        e1 = gt_graph.add_edge(v1, v2)
        e2 = gt_graph.add_edge(v2, v3)
        
        weight = gt_graph.new_edge_property("double")
        weight[e1] = 5.0
        weight[e2] = 3.0
        gt_graph.ep["weight"] = weight

        # Convert to our graph
        graph = GraphToolAdapter.from_graph_tool(gt_graph)

        assert graph.vertex_count() == 3
        assert graph.edge_count() == 2
        assert graph.has_vertex("A")
        assert graph.has_edge("A", "B")

    def test_from_graph_tool_preserves_weights(self) -> None:
        """Test that weights are preserved when converting from graph-tool."""
        import graph_tool.all as gt

        gt_graph = gt.Graph()
        v1 = gt_graph.add_vertex()
        v2 = gt_graph.add_vertex()
        e = gt_graph.add_edge(v1, v2)
        
        weight = gt_graph.new_edge_property("double")
        weight[e] = 7.5
        gt_graph.ep["weight"] = weight

        graph = GraphToolAdapter.from_graph_tool(gt_graph)

        edge = graph.get_edge(0, 1)
        assert edge.weight == 7.5

    def test_roundtrip_conversion(self, sample_graph: SimpleGraph) -> None:
        """Test that our_graph -> graph-tool -> our_graph preserves structure."""
        # Convert to graph-tool and back
        gt_graph = GraphToolAdapter.to_graph_tool(sample_graph)
        restored = GraphToolAdapter.from_graph_tool(gt_graph)

        # Check structure preserved
        assert restored.vertex_count() == sample_graph.vertex_count()
        assert restored.edge_count() == sample_graph.edge_count()

        # Check vertices
        original_vertices = {v.id for v in sample_graph.vertices()}
        restored_vertices = {v.id for v in restored.vertices()}
        assert original_vertices == restored_vertices

    def test_python_type_mapping(self) -> None:
        """Test Python type to graph-tool type mapping."""
        assert GraphToolAdapter._python_type_to_graph_tool(bool) == "bool"
        assert GraphToolAdapter._python_type_to_graph_tool(int) == "int"
        assert GraphToolAdapter._python_type_to_graph_tool(float) == "double"
        assert GraphToolAdapter._python_type_to_graph_tool(str) == "string"
        assert GraphToolAdapter._python_type_to_graph_tool(list) == "vector<double>"


class TestGraphToolVisualization:
    """Test graph-tool visualization capabilities."""

    @pytest.fixture
    def sample_graph(self) -> SimpleGraph:
        """Create sample graph for visualization."""
        graph = SimpleGraph()
        for i in range(5):
            graph.add_vertex(i)

        edges = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 0), (1, 3)]
        for source, target in edges:
            graph.add_edge(source, target, weight=1.0)

        return graph

    def test_visualize_with_output_file(
        self,
        sample_graph: SimpleGraph,
        tmp_path: Path,
    ) -> None:
        """Test visualization with file output."""
        output_file = tmp_path / "test_graph.pdf"
        
        GraphToolAdapter.visualize(
            sample_graph,
            output=output_file,
            layout="sfdp",
        )

        assert output_file.exists()

    def test_visualize_different_layouts(
        self,
        sample_graph: SimpleGraph,
        tmp_path: Path,
    ) -> None:
        """Test different layout algorithms."""
        layouts = ["sfdp", "fr", "arf", "random", "radial"]

        for layout in layouts:
            output_file = tmp_path / f"layout_{layout}.pdf"
            
            GraphToolAdapter.visualize(
                sample_graph,
                output=output_file,
                layout=layout,
            )

            assert output_file.exists()

    def test_visualize_custom_vertex_size(
        self,
        sample_graph: SimpleGraph,
        tmp_path: Path,
    ) -> None:
        """Test custom vertex size."""
        output_file = tmp_path / "custom_size.pdf"
        
        GraphToolAdapter.visualize(
            sample_graph,
            output=output_file,
            vertex_size=25,
        )

        assert output_file.exists()

    def test_visualize_custom_colors(
        self,
        sample_graph: SimpleGraph,
        tmp_path: Path,
    ) -> None:
        """Test custom vertex and edge colors."""
        output_file = tmp_path / "custom_colors.pdf"
        
        GraphToolAdapter.visualize(
            sample_graph,
            output=output_file,
            vertex_fill_color="lightblue",
            edge_color="gray",
        )

        assert output_file.exists()

    def test_visualize_no_vertex_labels(
        self,
        sample_graph: SimpleGraph,
        tmp_path: Path,
    ) -> None:
        """Test visualization without vertex labels."""
        output_file = tmp_path / "no_labels.pdf"
        
        GraphToolAdapter.visualize(
            sample_graph,
            output=output_file,
            vertex_text=False,
        )

        assert output_file.exists()

    def test_visualize_invalid_layout_raises(
        self,
        sample_graph: SimpleGraph,
    ) -> None:
        """Test that invalid layout raises error."""
        with pytest.raises(ValueError, match="Unsupported layout"):
            GraphToolAdapter.visualize(
                sample_graph,
                layout="invalid_layout",
            )

    def test_visualize_svg_output(
        self,
        sample_graph: SimpleGraph,
        tmp_path: Path,
    ) -> None:
        """Test SVG output format."""
        output_file = tmp_path / "graph.svg"
        
        GraphToolAdapter.visualize(
            sample_graph,
            output=output_file,
        )

        assert output_file.exists()

    def test_visualize_png_output(
        self,
        sample_graph: SimpleGraph,
        tmp_path: Path,
    ) -> None:
        """Test PNG output format."""
        output_file = tmp_path / "graph.png"
        
        GraphToolAdapter.visualize(
            sample_graph,
            output=output_file,
        )

        assert output_file.exists()


class TestGraphToolVisualizer:
    """Test GraphToolVisualizer high-level interface."""

    @pytest.fixture
    def sample_graph(self) -> SimpleGraph:
        """Create sample graph."""
        graph = SimpleGraph()
        for i in range(6):
            graph.add_vertex(i)

        edges = [(0, 1, 2.0), (1, 2, 3.0), (2, 3, 1.0), (3, 4, 4.0), (4, 5, 2.0), (5, 0, 1.0)]
        for source, target, weight in edges:
            graph.add_edge(source, target, weight=weight)

        return graph

    def test_visualizer_creation(self, sample_graph: SimpleGraph) -> None:
        """Test creating visualizer."""
        viz = GraphToolVisualizer(sample_graph)
        
        assert viz.graph == sample_graph
        assert viz.gt_graph is not None
        assert viz.gt_graph.num_vertices() == 6

    def test_basic_plot(
        self,
        sample_graph: SimpleGraph,
        tmp_path: Path,
    ) -> None:
        """Test basic plot method."""
        viz = GraphToolVisualizer(sample_graph)
        output_file = tmp_path / "basic.pdf"
        
        viz.basic_plot(output=output_file)
        
        assert output_file.exists()
        assert viz.pos is not None  # Layout was computed

    def test_degree_colored_plot(
        self,
        sample_graph: SimpleGraph,
        tmp_path: Path,
    ) -> None:
        """Test degree-colored plot."""
        viz = GraphToolVisualizer(sample_graph)
        output_file = tmp_path / "degree.pdf"
        
        viz.degree_colored_plot(output=output_file)
        
        assert output_file.exists()

    def test_weighted_plot(
        self,
        sample_graph: SimpleGraph,
        tmp_path: Path,
    ) -> None:
        """Test weighted plot."""
        viz = GraphToolVisualizer(sample_graph)
        output_file = tmp_path / "weighted.pdf"
        
        viz.weighted_plot(output=output_file)
        
        assert output_file.exists()

    def test_weighted_plot_no_weights_raises(self) -> None:
        """Test that weighted plot without weights raises error."""
        # Create graph without weights
        graph = SimpleGraph()
        graph.add_vertex("A")
        graph.add_vertex("B")
        # Don't add edges or add without weight attribute
        
        viz = GraphToolVisualizer(graph)
        
        with pytest.raises(ValueError, match="no edge weights"):
            viz.weighted_plot()

    def test_community_plot(
        self,
        sample_graph: SimpleGraph,
        tmp_path: Path,
    ) -> None:
        """Test community detection plot."""
        viz = GraphToolVisualizer(sample_graph)
        output_file = tmp_path / "communities.pdf"
        
        viz.community_plot(output=output_file)
        
        assert output_file.exists()

    def test_layout_persistence(
        self,
        sample_graph: SimpleGraph,
        tmp_path: Path,
    ) -> None:
        """Test that layout is computed once and reused."""
        viz = GraphToolVisualizer(sample_graph)
        
        assert viz.pos is None
        
        viz.basic_plot(output=tmp_path / "plot1.pdf")
        first_pos = viz.pos
        
        assert first_pos is not None
        
        viz.basic_plot(output=tmp_path / "plot2.pdf")
        second_pos = viz.pos
        
        # Same layout should be reused
        assert first_pos is second_pos


class TestGraphToolAvailability:
    """Test graph-tool availability handling."""

    def test_graph_tool_available_flag(self) -> None:
        """Test that GRAPH_TOOL_AVAILABLE flag is correct."""
        # This test runs only if graph-tool is installed
        assert GRAPH_TOOL_AVAILABLE is True

    def test_adapter_check(self) -> None:
        """Test that adapter doesn't raise when graph-tool available."""
        # Should not raise
        GraphToolAdapter._check_graph_tool_available()


class TestComplexGraphs:
    """Test with more complex graph structures."""

    def test_large_graph(self, tmp_path: Path) -> None:
        """Test visualization of larger graph."""
        graph = SimpleGraph()
        
        # Create a larger graph (50 vertices)
        for i in range(50):
            graph.add_vertex(i)
        
        # Add edges in a pattern
        for i in range(49):
            graph.add_edge(i, i + 1, weight=1.0)
        
        # Add some random connections
        import random
        random.seed(42)
        for _ in range(30):
            source = random.randint(0, 49)
            target = random.randint(0, 49)
            if source != target and not graph.has_edge(source, target):
                graph.add_edge(source, target, weight=0.5)

        output_file = tmp_path / "large_graph.pdf"
        GraphToolAdapter.visualize(graph, output=output_file)
        
        assert output_file.exists()

    def test_disconnected_graph(self, tmp_path: Path) -> None:
        """Test visualization of disconnected graph."""
        graph = SimpleGraph()
        
        # Component 1
        for i in range(5):
            graph.add_vertex(f"A{i}")
        for i in range(4):
            graph.add_edge(f"A{i}", f"A{i+1}")
        
        # Component 2 (disconnected)
        for i in range(5):
            graph.add_vertex(f"B{i}")
        for i in range(4):
            graph.add_edge(f"B{i}", f"B{i+1}")

        output_file = tmp_path / "disconnected.pdf"
        GraphToolAdapter.visualize(graph, output=output_file)
        
        assert output_file.exists()

    def test_star_graph(self, tmp_path: Path) -> None:
        """Test visualization of star graph."""
        graph = SimpleGraph()
        
        # Create star with center and 10 leaves
        graph.add_vertex("center")
        for i in range(10):
            graph.add_vertex(f"leaf{i}")
            graph.add_edge("center", f"leaf{i}", weight=1.0)

        output_file = tmp_path / "star.pdf"
        GraphToolAdapter.visualize(
            graph,
            output=output_file,
            layout="radial",
        )
        
        assert output_file.exists()
