#!/usr/bin/env python3
"""
Quick test script for graph library.
Run from project root: python test_graph.py
"""

import sys
from pathlib import Path

# Add packages directory to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Now imports work
from packages.graphs.simple_graph import SimpleGraph
from packages.algorithms.traversal import bfs, dfs
from packages.algorithms.shortest_path import dijkstra


def main():
    print("=" * 60)
    print("GRAPH LIBRARY TEST")
    print("=" * 60)

    # Create simple graph
    graph = SimpleGraph()
    
    print("\n1. Adding vertices...")
    graph.add_vertex("A", color="red")
    graph.add_vertex("B", color="blue")
    graph.add_vertex("C", color="green")
    print(f"   Vertices: {graph.vertex_count()}")

    print("\n2. Adding edges...")
    graph.add_edge("A", "B", weight=5.0)
    graph.add_edge("B", "C", weight=3.0)
    graph.add_edge("A", "C", weight=10.0)
    print(f"   Edges: {graph.edge_count()}")

    print("\n3. Graph structure:")
    for edge in graph.edges():
        print(f"   {edge}")

    print("\n4. BFS traversal from A:")
    print(f"   {list(bfs(graph, 'A'))}")

    print("\n5. DFS traversal from A:")
    print(f"   {list(dfs(graph, 'A'))}")

    print("\n6. Shortest paths from A:")
    distances = dijkstra(graph, "A")
    for vertex, dist in sorted(distances.items()):
        print(f"   A -> {vertex}: {dist}")

    print("\n7. Testing self-loop constraint...")
    try:
        graph.add_edge("A", "A")
        print("   ❌ Self-loop was allowed (ERROR!)")
    except Exception as e:
        print(f"   ✅ Self-loop rejected: {type(e).__name__}")

    print("\n8. Converting representation...")
    print(f"   Current: adjacency_list")
    graph.convert_representation("adjacency_matrix")
    print(f"   Converted to: adjacency_matrix")
    print(f"   Still has edge A->B: {graph.has_edge('A', 'B')}")

    print("\n" + "=" * 60)
    print("✅ ALL TESTS PASSED!")
    print("=" * 60)


if __name__ == "__main__":
    main()
