"""
Comprehensive examples demonstrating all graph library features.

This module showcases:
- Creating different graph types
- Converting between representations
- Converting between graph types
- Running algorithms
- Working with attributes
- Integration with NetworkX
"""

from __future__ import annotations


def example_simple_graph() -> None:
    """Demonstrate simple graph operations."""
    from packages.graphs.simple_graph import SimpleGraph

    print("=" * 60)
    print("SIMPLE GRAPH EXAMPLE")
    print("=" * 60)

    # Create undirected simple graph
    graph = SimpleGraph(representation="adjacency_list")

    # Add vertices with attributes
    graph.add_vertex("A", color="red", weight=10)
    graph.add_vertex("B", color="blue", weight=20)
    graph.add_vertex("C", color="green", weight=15)
    graph.add_vertex("D", color="yellow", weight=25)

    # Add edges with weights
    graph.add_edge("A", "B", weight=5.0, label="road")
    graph.add_edge("B", "C", weight=3.0, label="path")
    graph.add_edge("C", "D", weight=4.0, label="trail")
    graph.add_edge("A", "C", weight=10.0, label="highway")

    print(f"\nGraph: {graph}")
    print(f"Vertices: {graph.vertex_count()}")
    print(f"Edges: {graph.edge_count()}")

    # Display vertices
    print("\nVertices:")
    for vertex in graph.vertices():
        print(f"  {vertex.id}: {vertex.attributes}")

    # Display edges
    print("\nEdges:")
    for edge in graph.edges():
        print(f"  {edge}")

    # Get neighbors
    print(f"\nNeighbors of 'A': {sorted(graph.get_neighbors('A'))}")
    print(f"Degree of 'C': {graph.degree('C')}")

    # Try to add self-loop (will fail)
    try:
        graph.add_edge("A", "A", weight=1.0)
    except Exception as e:
        print(f"\n✗ Self-loop rejected: {e}")

    print()


def example_representation_conversion() -> None:
    """Demonstrate converting between representations."""
    from packages.graphs.simple_graph import SimpleGraph

    print("=" * 60)
    print("REPRESENTATION CONVERSION EXAMPLE")
    print("=" * 60)

    # Create graph with adjacency list
    graph = SimpleGraph(representation="adjacency_list")
    graph.add_vertex("A")
    graph.add_vertex("B")
    graph.add_vertex("C")
    graph.add_edge("A", "B", weight=2.0)
    graph.add_edge("B", "C", weight=3.0)
    graph.add_edge("A", "C", weight=7.0)

    print(f"\nInitial representation: adjacency_list")
    print(f"Graph: {graph}")

    # Convert to adjacency matrix
    graph.convert_representation("adjacency_matrix")
    print(f"\nConverted to: adjacency_matrix")
    print(f"Graph: {graph}")

    # Operations still work
    print(f"Has edge A->C: {graph.has_edge('A', 'C')}")
    print(f"Neighbors of B: {sorted(graph.get_neighbors('B'))}")

    print()


def example_multigraph() -> None:
    """Demonstrate multigraph with parallel edges."""
    from packages.graphs.multigraph import Multigraph

    print("=" * 60)
    print("MULTIGRAPH EXAMPLE")
    print("=" * 60)

    # Create multigraph
    multi = Multigraph()

    # Add vertices
    multi.add_vertex("A")
    multi.add_vertex("B")

    # Add multiple edges between same vertices
    multi.add_edge("A", "B", weight=3.0, label="route1")
    multi.add_edge("A", "B", weight=5.0, label="route2")
    multi.add_edge("A", "B", weight=2.0, label="route3")

    print(f"\nMultigraph: {multi}")
    print(f"Edge count: {multi.edge_count()}")
    print(f"Edge multiplicity A->B: {multi.edge_multiplicity('A', 'B')}")

    print("\nAll edges:")
    for edge in multi.edges():
        print(f"  {edge} - {edge.attributes}")

    # Try to add self-loop (will fail in multigraph)
    try:
        multi.add_edge("A", "A", weight=1.0)
    except Exception as e:
        print(f"\n✗ Self-loop rejected: {e}")

    print()


def example_graph_algorithms() -> None:
    """Demonstrate graph algorithms."""
    from packages.algorithms.shortest_path import dijkstra, reconstruct_path
    from packages.algorithms.traversal import bfs, dfs, is_connected
    from packages.graphs.simple_graph import SimpleGraph

    print("=" * 60)
    print("GRAPH ALGORITHMS EXAMPLE")
    print("=" * 60)

    # Create graph
    graph = SimpleGraph()
    for vertex in ["A", "B", "C", "D", "E"]:
        graph.add_vertex(vertex)

    graph.add_edge("A", "B", weight=4.0)
    graph.add_edge("A", "C", weight=2.0)
    graph.add_edge("B", "C", weight=1.0)
    graph.add_edge("B", "D", weight=5.0)
    graph.add_edge("C", "D", weight=8.0)
    graph.add_edge("C", "E", weight=10.0)
    graph.add_edge("D", "E", weight=2.0)

    print("\nGraph structure:")
    for edge in graph.edges():
        print(f"  {edge}")

    # BFS traversal
    print(f"\nBFS from 'A': {list(bfs(graph, 'A'))}")

    # DFS traversal
    print(f"DFS from 'A': {list(dfs(graph, 'A'))}")

    # Check connectivity
    print(f"\nIs connected: {is_connected(graph)}")

    # Dijkstra's shortest path
    distances, predecessors = dijkstra(graph, "A", "E")
    print(f"\nShortest distance A->E: {distances['E']}")

    path = reconstruct_path(predecessors, "A", "E")
    print(f"Shortest path A->E: {' -> '.join(path)}")

    # All distances from A
    all_distances = dijkstra(graph, "A")
    print("\nDistances from A:")
    for vertex, dist in sorted(all_distances.items()):
        print(f"  {vertex}: {dist}")

    print()


def example_graph_type_conversion() -> None:
    """Demonstrate converting between graph types."""
    from packages.converters.graph_converters import multigraph_to_simple
    from packages.graphs.multigraph import Multigraph

    print("=" * 60)
    print("GRAPH TYPE CONVERSION EXAMPLE")
    print("=" * 60)

    # Create multigraph with parallel edges
    multi = Multigraph()
    multi.add_vertex("A")
    multi.add_vertex("B")
    multi.add_vertex("C")

    multi.add_edge("A", "B", weight=3.0)
    multi.add_edge("A", "B", weight=7.0)
    multi.add_edge("A", "B", weight=5.0)
    multi.add_edge("B", "C", weight=2.0)

    print(f"\nOriginal multigraph: {multi}")
    print(f"Edge count: {multi.edge_count()}")
    print(f"Multiplicity A->B: {multi.edge_multiplicity('A', 'B')}")

    # Convert to simple graph (merge parallel edges)
    simple_min = multigraph_to_simple(multi, merge_strategy="min")
    print(f"\nConverted to simple (min weight): {simple_min}")
    for edge in simple_min.edges():
        if edge.source == "A" and edge.target == "B":
            print(f"  Merged edge A->B weight: {edge.weight}")

    simple_avg = multigraph_to_simple(multi, merge_strategy="avg")
    print(f"\nConverted to simple (avg weight): {simple_avg}")
    for edge in simple_avg.edges():
        if edge.source == "A" and edge.target == "B":
            print(f"  Merged edge A->B weight: {edge.weight}")

    print()


def main() -> None:
    """Run all examples."""
    example_simple_graph()
    example_representation_conversion()
    example_multigraph()
    example_graph_algorithms()
    example_graph_type_conversion()

    print("=" * 60)
    print("ALL EXAMPLES COMPLETED SUCCESSFULLY!")
    print("=" * 60)


if __name__ == "__main__":
    main()
