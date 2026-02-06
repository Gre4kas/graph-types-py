"""
Demonstration of graph-tool visualization capabilities.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from packages.graphs.simple_graph import SimpleGraph
from packages.integrations.graph_tool_adapter import (
    GRAPH_TOOL_AVAILABLE,
    GraphToolAdapter,
    GraphToolVisualizer,
)


def demo_basic_visualization():
    """Demonstrate basic graph visualization."""
    print("=" * 60)
    print("BASIC GRAPH VISUALIZATION")
    print("=" * 60)

    if not GRAPH_TOOL_AVAILABLE:
        print("\n⚠️  graph-tool not installed!")
        print("Install with: conda install -c conda-forge graph-tool")
        return

    # Create simple social network
    graph = SimpleGraph()
    people = ["Alice", "Bob", "Charlie", "David", "Eve"]
    for person in people:
        graph.add_vertex(person)

    connections = [
        ("Alice", "Bob"), ("Alice", "Charlie"),
        ("Bob", "David"), ("Charlie", "David"),
        ("David", "Eve"),
    ]
    for source, target in connections:
        graph.add_edge(source, target, weight=1.0)

    print(f"\n1. Created social network:")
    print(f"   People: {graph.vertex_count()}")
    print(f"   Connections: {graph.edge_count()}")

    # Visualize with different layouts
    layouts = ["sfdp", "fr", "radial"]
    for layout in layouts:
        output = f"output/basic_{layout}.pdf"
        print(f"\n2. Generating {layout} layout → {output}")
        GraphToolAdapter.visualize(
            graph,
            output=output,
            layout=layout,
            vertex_size=30,
            vertex_font_size=14,
        )

    print("\n✅ Basic visualizations created!")


def demo_styled_visualization():
    """Demonstrate custom styling."""
    print("\n" + "=" * 60)
    print("STYLED VISUALIZATION")
    print("=" * 60)

    if not GRAPH_TOOL_AVAILABLE:
        print("\n⚠️  graph-tool not installed!")
        return

    # Create graph with attributes
    graph = SimpleGraph()
    
    # Add vertices with colors
    graph.add_vertex("Manager", role="management", color="red")
    graph.add_vertex("Dev1", role="developer", color="blue")
    graph.add_vertex("Dev2", role="developer", color="blue")
    graph.add_vertex("Designer", role="designer", color="green")
    graph.add_vertex("QA", role="qa", color="orange")

    # Add weighted edges (collaboration strength)
    edges = [
        ("Manager", "Dev1", 5.0),
        ("Manager", "Dev2", 4.0),
        ("Manager", "Designer", 3.0),
        ("Dev1", "Dev2", 8.0),
        ("Dev1", "Designer", 6.0),
        ("Dev2", "QA", 7.0),
        ("Designer", "QA", 5.0),
    ]
    for source, target, weight in edges:
        graph.add_edge(source, target, weight=weight)

    print(f"\n1. Created team collaboration graph:")
    print(f"   Team members: {graph.vertex_count()}")
    print(f"   Collaborations: {graph.edge_count()}")

    # Visualize with custom styling
    print(f"\n2. Generating styled visualization...")
    
    GraphToolAdapter.visualize(
        graph,
        output="output/styled_team.pdf",
        layout="sfdp",
        vertex_size=40,
        vertex_fill_color="color",  # Use color attribute
        vertex_text=True,
        vertex_font_size=12,
        edge_pen_width=None,  # Use weight-based width
    )

    print("✅ Styled visualization created!")


def demo_high_level_visualizer():
    """Demonstrate GraphToolVisualizer high-level interface."""
    print("\n" + "=" * 60)
    print("HIGH-LEVEL VISUALIZER")
    print("=" * 60)

    if not GRAPH_TOOL_AVAILABLE:
        print("\n⚠️  graph-tool not installed!")
        return

    # Create a more complex network
    graph = SimpleGraph()
    
    # Create 20 vertices
    for i in range(20):
        graph.add_vertex(i)
    
    # Add edges with varying weights
    import random
    random.seed(42)
    for i in range(40):
        source = random.randint(0, 19)
        target = random.randint(0, 19)
        if source != target and not graph.has_edge(source, target):
            weight = random.uniform(1.0, 10.0)
            graph.add_edge(source, target, weight=weight)

    print(f"\n1. Created random network:")
    print(f"   Vertices: {graph.vertex_count()}")
    print(f"   Edges: {graph.edge_count()}")

    # Use high-level visualizer
    viz = GraphToolVisualizer(graph)

    print(f"\n2. Generating different visualizations...")

    # Basic plot
    print("   - Basic plot")
    viz.basic_plot(output="output/highlevel_basic.pdf")

    # Degree-colored plot
    print("   - Degree-colored plot")
    viz.degree_colored_plot(output="output/highlevel_degree.pdf")

    # Weighted plot
    print("   - Weighted plot (edge thickness = weight)")
    viz.weighted_plot(output="output/highlevel_weighted.pdf")

    # Community plot
    print("   - Community detection plot")
    viz.community_plot(output="output/highlevel_communities.pdf")

    print("\n✅ All high-level visualizations created!")


def demo_large_graph():
    """Demonstrate visualization of larger graph."""
    print("\n" + "=" * 60)
    print("LARGE GRAPH VISUALIZATION")
    print("=" * 60)

    if not GRAPH_TOOL_AVAILABLE:
        print("\n⚠️  graph-tool not installed!")
        return

    # Create larger graph (100 vertices)
    graph = SimpleGraph()
    
    print(f"\n1. Creating large random graph...")
    for i in range(100):
        graph.add_vertex(i)
    
    # Add random edges
    import random
    random.seed(42)
    for _ in range(200):
        source = random.randint(0, 99)
        target = random.randint(0, 99)
        if source != target and not graph.has_edge(source, target):
            graph.add_edge(source, target, weight=1.0)

    print(f"   Vertices: {graph.vertex_count()}")
    print(f"   Edges: {graph.edge_count()}")

    print(f"\n2. Generating visualization...")
    print("   (This may take a few seconds for large graphs)")

    GraphToolAdapter.visualize(
        graph,
        output="output/large_graph.pdf",
        layout="sfdp",
        vertex_size=8,
        vertex_text=False,  # Hide labels for clarity
        edge_pen_width=1.0,
    )

    print("\n✅ Large graph visualization created!")


def demo_different_formats():
    """Demonstrate different output formats."""
    print("\n" + "=" * 60)
    print("DIFFERENT OUTPUT FORMATS")
    print("=" * 60)

    if not GRAPH_TOOL_AVAILABLE:
        print("\n⚠️  graph-tool not installed!")
        return

    # Create simple graph
    graph = SimpleGraph()
    for i in range(5):
        graph.add_vertex(i)
    
    edges = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 0)]
    for source, target in edges:
        graph.add_edge(source, target, weight=1.0)

    print(f"\n1. Creating visualizations in different formats...")

    formats = [
        ("pdf", "output/format_test.pdf"),
        ("svg", "output/format_test.svg"),
        ("png", "output/format_test.png"),
    ]

    for fmt, output in formats:
        print(f"   - {fmt.upper()}: {output}")
        GraphToolAdapter.visualize(
            graph,
            output=output,
            vertex_size=25,
        )

    print("\n✅ All formats created!")


def demo_karate_club():
    """Demonstrate with Zachary's Karate Club graph."""
    print("\n" + "=" * 60)
    print("KARATE CLUB GRAPH")
    print("=" * 60)

    if not GRAPH_TOOL_AVAILABLE:
        print("\n⚠️  graph-tool not installed!")
        return

    try:
        import networkx as nx
        from packages.integrations.networkx_adapter import NetworkXAdapter
    except ImportError:
        print("\n⚠️  NetworkX not installed! Skipping this demo.")
        return

    # Load Karate Club from NetworkX
    print(f"\n1. Loading Zachary's Karate Club graph...")
    nx_karate = nx.karate_club_graph()
    graph = NetworkXAdapter.from_networkx(nx_karate)

    print(f"   Members: {graph.vertex_count()}")
    print(f"   Interactions: {graph.edge_count()}")

    # Visualize with community detection
    print(f"\n2. Visualizing with community detection...")
    viz = GraphToolVisualizer(graph)
    viz.community_plot(output="output/karate_communities.pdf", layout="sfdp")

    print(f"\n3. Visualizing with degree coloring...")
    viz.degree_colored_plot(output="output/karate_degree.pdf", layout="sfdp")

    print("\n✅ Karate Club visualizations created!")


def create_output_directory():
    """Create output directory if it doesn't exist."""
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)


if __name__ == "__main__":
    create_output_directory()

    demo_basic_visualization()
    demo_styled_visualization()
    demo_high_level_visualizer()
    demo_large_graph()
    demo_different_formats()
    demo_karate_club()

    print("\n" + "=" * 60)
    print("✅ ALL GRAPH-TOOL DEMOS COMPLETED!")
    print("=" * 60)
    print("\nCheck the 'output/' directory for generated visualizations.")
