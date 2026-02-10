"""
Pseudograph Example for graph-types-py

Demonstrates:
- Creating a pseudograph (allows self-loops)
- Modeling network topology with local loops
- Self-loop operations (edges from vertex to itself)
- Converting to adjacency matrix with self-loops
"""

from packages.graphs.pseudograph import Pseudograph
from packages.representations.adjacency_matrix import to_adjacency_matrix
from packages.algorithms.shortest_path import dijkstra


def main():
    # Create a pseudograph representing a network with local loops
    graph = Pseudograph(directed=True)
    
    # Add vertices (network nodes/intersections)
    nodes = ["Center", "North", "South", "East", "West", "Hub"]
    for node in nodes:
        graph.add_vertex(node)
    
    # Add regular edges (connections between different nodes)
    connections = [
        ("Center", "North", 10),
        ("Center", "South", 15),
        ("Center", "East", 12),
        ("North", "Hub", 8),
        ("South", "Hub", 10),
        ("East", "West", 7),
        ("West", "Hub", 9),
    ]
    
    for source, target, weight in connections:
        graph.add_edge(source, target, weight=weight)
    
    # Add self-loops (local circular routes or maintenance loops)
    self_loops = [
        ("Center", "Center", 5),  # City center circular route
        ("Hub", "Hub", 3),        # Hub terminal loop
        ("North", "North", 4),    # North district loop
    ]
    
    print("=== Pseudograph with Self-Loops ===")
    for source, target, weight in self_loops:
        graph.add_edge(source, target, weight=weight)
        print(f"Added self-loop at {source} (weight: {weight})")
    
    print(f"\nTotal vertices: {len(graph.get_vertices())}")
    print(f"Total edges: {graph.edge_count()}")
    print(f"Self-loops count: {graph.count_self_loops()}\n")
    
    # List all self-loops
    print("=== Self-Loops in Graph ===")
    for vertex in graph.get_vertices():
        if graph.has_self_loop(vertex):
            loop_weight = graph.get_edge_weight(vertex, vertex)
            print(f"{vertex} -> {vertex} (weight: {loop_weight})")
    
    # Convert to adjacency matrix (self-loops appear on diagonal)
    print("\n=== Adjacency Matrix (note diagonal elements) ===")
    adj_matrix = to_adjacency_matrix(graph)
    print("Vertex order:", graph.get_vertices())
    print(adj_matrix)
    print("\nNon-zero diagonal elements indicate self-loops\n")
    
    # Find shortest path from Center to Hub
    print("=== Shortest Path (Dijkstra) ===")
    distances = dijkstra(graph, "Center")
    print(f"Distances from Center: {distances}")


if __name__ == "__main__":
    main()
