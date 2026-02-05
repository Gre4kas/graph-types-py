"""
Demonstration of NetworkX integration.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from packages.graphs.simple_graph import SimpleGraph
from packages.integrations.networkx_adapter import (
    NETWORKX_AVAILABLE,
    NetworkXAdapter,
    NetworkXAlgorithms,
)

def demo_basic_conversion():
    """Demonstrate basic conversion to/from NetworkX."""
    print("=" * 60)
    print("BASIC NETWORKX CONVERSION")
    print("=" * 60)

    if not NETWORKX_AVAILABLE:
        print("\n⚠️  NetworkX not installed!")
        print("Install with: pip install networkx")
        return

    # Create our graph
    graph = SimpleGraph()
    graph.add_vertex("Alice", age=30, role="manager")
    graph.add_vertex("Bob", age=25, role="developer")
    graph.add_vertex("Charlie", age=28, role="designer")
    graph.add_edge("Alice", "Bob", weight=5.0, relationship="supervises")
    graph.add_edge("Bob", "Charlie", weight=3.0, relationship="collaborates")

    print("\n1. Our graph:")
    print(f"   Vertices: {graph.vertex_count()}")
    print(f"   Edges: {graph.edge_count()}")

    # Convert to NetworkX
    nx_graph = NetworkXAdapter.to_networkx(graph)
    print(f"\n2. Converted to NetworkX:")
    print(f"   Type: {type(nx_graph).__name__}")
    print(f"   Nodes: {nx_graph.number_of_nodes()}")
    print(f"   Edges: {nx_graph.number_of_edges()}")

    # Convert back
    restored = NetworkXAdapter.from_networkx(nx_graph)
    print(f"\n3. Converted back:")
    print(f"   Vertices: {restored.vertex_count()}")
    print(f"   Edges: {restored.edge_count()}")
    print(f"   ✅ Roundtrip successful!")


def demo_famous_graphs():
    """Demonstrate with NetworkX's famous graphs."""
    print("\n" + "=" * 60)
    print("FAMOUS NETWORKX GRAPHS")
    print("=" * 60)

    if not NETWORKX_AVAILABLE:
        print("\n⚠️  NetworkX not installed!")
        return

    import networkx as nx

    # Zachary's Karate Club
    print("\n1. Zachary's Karate Club Graph:")
    nx_karate = nx.karate_club_graph()
    karate = NetworkXAdapter.from_networkx(nx_karate)
    print(f"   Vertices: {karate.vertex_count()}")
    print(f"   Edges: {karate.edge_count()}")

    # Les Misérables character network
    print("\n2. Les Misérables Graph:")
    nx_lesmis = nx.les_miserables_graph()
    lesmis = NetworkXAdapter.from_networkx(nx_lesmis)
    print(f"   Vertices: {lesmis.vertex_count()}")
    print(f"   Edges: {lesmis.edge_count()}")

    # Davis Southern Women
    print("\n3. Davis Southern Women Graph:")
    nx_davis = nx.davis_southern_women_graph()
    davis = NetworkXAdapter.from_networkx(nx_davis)
    print(f"   Vertices: {davis.vertex_count()}")
    print(f"   Edges: {davis.edge_count()}")


def demo_centrality_analysis():
    """Demonstrate centrality analysis using NetworkX."""
    print("\n" + "=" * 60)
    print("CENTRALITY ANALYSIS")
    print("=" * 60)

    if not NETWORKX_AVAILABLE:
        print("\n⚠️  NetworkX not installed!")
        return

    # Create social network
    graph = SimpleGraph()
    people = ["Alice", "Bob", "Charlie", "David", "Eve", "Frank"]
    for person in people:
        graph.add_vertex(person)

    # Add connections
    connections = [
        ("Alice", "Bob"), ("Alice", "Charlie"), ("Alice", "David"),
        ("Bob", "Charlie"), ("Bob", "Eve"),
        ("Charlie", "David"), ("Charlie", "Frank"),
        ("David", "Eve"),
        ("Eve", "Frank"),
    ]
    for source, target in connections:
        graph.add_edge(source, target, weight=1.0)

    print(f"\n1. Social network:")
    print(f"   People: {graph.vertex_count()}")
    print(f"   Connections: {graph.edge_count()}")

    # Betweenness centrality
    print(f"\n2. Betweenness Centrality (bridge nodes):")
    betweenness = NetworkXAlgorithms.betweenness_centrality(graph)
    sorted_betweenness = sorted(
        betweenness.items(),
        key=lambda x: x[1],
        reverse=True,
    )
    for person, score in sorted_betweenness[:3]:
        print(f"   {person}: {score:.3f}")

    # PageRank
    print(f"\n3. PageRank (influence):")
    pagerank = NetworkXAlgorithms.pagerank(graph)
    sorted_pagerank = sorted(
        pagerank.items(),
        key=lambda x: x[1],
        reverse=True,
    )
    for person, score in sorted_pagerank[:3]:
        print(f"   {person}: {score:.3f}")

    # Clustering coefficient
    print(f"\n4. Clustering Coefficient (tight-knit groups):")
    clustering = NetworkXAlgorithms.clustering_coefficient(graph)
    sorted_clustering = sorted(
        clustering.items(),
        key=lambda x: x[1],
        reverse=True,
    )
    for person, score in sorted_clustering[:3]:
        print(f"   {person}: {score:.3f}")


def demo_community_detection():
    """Demonstrate community detection."""
    print("\n" + "=" * 60)
    print("COMMUNITY DETECTION")
    print("=" * 60)

    if not NETWORKX_AVAILABLE:
        print("\n⚠️  NetworkX not installed!")
        return

    # Create graph with obvious communities
    graph = SimpleGraph()

    # Community 1
    for i in range(5):
        graph.add_vertex(f"A{i}")
    for i in range(4):
        graph.add_edge(f"A{i}", f"A{i+1}")

    # Community 2
    for i in range(5):
        graph.add_vertex(f"B{i}")
    for i in range(4):
        graph.add_edge(f"B{i}", f"B{i+1}")

    # Bridge between communities
    graph.add_edge("A2", "B2", weight=0.5)

    print(f"\n1. Graph with 2 communities:")
    print(f"   Vertices: {graph.vertex_count()}")
    print(f"   Edges: {graph.edge_count()}")

    # Detect communities
    communities = NetworkXAlgorithms.detect_communities(graph, method="greedy")

    print(f"\n2. Detected {len(communities)} communities:")
    for i, community in enumerate(communities, 1):
        print(f"   Community {i}: {sorted(community)}")


def demo_shortest_paths():
    """Demonstrate shortest path algorithms."""
    print("\n" + "=" * 60)
    print("SHORTEST PATHS")
    print("=" * 60)

    if not NETWORKX_AVAILABLE:
        print("\n⚠️  NetworkX not installed!")
        return

    # Create city network
    graph = SimpleGraph()
    cities = ["NYC", "LA", "Chicago", "Houston", "Phoenix"]
    for city in cities:
        graph.add_vertex(city)

    # Add routes with distances
    routes = [
        ("NYC", "Chicago", 790),
        ("NYC", "Houston", 1630),
        ("LA", "Phoenix", 370),
        ("LA", "Houston", 1550),
        ("Chicago", "Houston", 1080),
        ("Chicago", "Phoenix", 1750),
        ("Phoenix", "Houston", 1180),
    ]
    for source, target, distance in routes:
        graph.add_edge(source, target, weight=distance)

    print(f"\n1. City network:")
    print(f"   Cities: {graph.vertex_count()}")
    print(f"   Routes: {graph.edge_count()}")

    # Calculate all shortest paths
    paths = NetworkXAlgorithms.all_pairs_shortest_path(graph)

    print(f"\n2. Sample shortest paths:")
    print(f"   NYC → LA: {paths['NYC']['LA']}")
    print(f"   Chicago → Phoenix: {paths['Chicago']['Phoenix']}")


def demo_minimum_spanning_tree():
    """Demonstrate MST calculation."""
    print("\n" + "=" * 60)
    print("MINIMUM SPANNING TREE")
    print("=" * 60)

    if not NETWORKX_AVAILABLE:
        print("\n⚠️  NetworkX not installed!")
        return

    # Create graph
    graph = SimpleGraph()
    vertices = ["A", "B", "C", "D", "E"]
    for v in vertices:
        graph.add_vertex(v)

    # Add edges with weights
    edges = [
        ("A", "B", 2), ("A", "D", 5),
        ("B", "C", 3), ("B", "D", 1), ("B", "E", 4),
        ("C", "E", 1),
        ("D", "E", 2),
    ]
    for source, target, weight in edges:
        graph.add_edge(source, target, weight=weight)

    print(f"\n1. Original graph:")
    print(f"   Vertices: {graph.vertex_count()}")
    print(f"   Edges: {graph.edge_count()}")

    # Calculate MST
    mst = NetworkXAlgorithms.minimum_spanning_tree(graph)

    print(f"\n2. Minimum Spanning Tree:")
    print(f"   Vertices: {mst.vertex_count()}")
    print(f"   Edges: {mst.edge_count()}")

    # Show MST edges
    print(f"\n3. MST edges:")
    for edge in mst.edges():
        print(f"   {edge.source} -- {edge.target} (weight={edge.weight})")


if __name__ == "__main__":
    demo_basic_conversion()
    demo_famous_graphs()
    demo_centrality_analysis()
    demo_community_detection()
    demo_shortest_paths()
    demo_minimum_spanning_tree()

    print("\n" + "=" * 60)
    print("✅ ALL NETWORKX DEMOS COMPLETED!")
    print("=" * 60)
