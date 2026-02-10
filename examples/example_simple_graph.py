"""
Simple Graph Example for graph-types-py

Demonstrates:
- Creating a simple graph (no self-loops, no multiple edges)
- Adding vertices and edges representing a road network
- BFS traversal algorithm
- Converting between adjacency list and adjacency matrix representations
"""

from packages.graphs.simple_graph import SimpleGraph
from packages.algorithms.traversal import bfs
from packages.representations.adjacency_matrix import to_adjacency_matrix
from packages.representations.adjacency_list import to_adjacency_list


def main():
    # Create a simple graph representing Ukrainian cities connected by highways
    graph = SimpleGraph(directed=False)
    
    # Add vertices (cities)
    cities = ["Kyiv", "Lviv", "Odesa", "Kharkiv", "Dnipro", "Zaporizhzhia"]
    for city in cities:
        graph.add_vertex(city)
    
    # Add edges with weights (distances in km)
    connections = [
        ("Kyiv", "Lviv", 540),
        ("Kyiv", "Kharkiv", 480),
        ("Kyiv", "Odesa", 475),
        ("Kyiv", "Dnipro", 480),
        ("Lviv", "Odesa", 790),
        ("Dnipro", "Zaporizhzhia", 85),
        ("Kharkiv", "Dnipro", 220),
    ]
    
    for source, target, weight in connections:
        graph.add_edge(source, target, weight=weight)
    
    print("=== Simple Graph Structure ===")
    print(f"Vertices: {graph.get_vertices()}")
    print(f"Number of edges: {graph.edge_count()}")
    print(f"Edges: {graph.get_edges()}\n")
    
    # Perform BFS traversal starting from Kyiv
    print("=== BFS Traversal from Kyiv ===")
    bfs_order = list(bfs(graph, "Kyiv"))
    print(f"Order: {' -> '.join(str(v) for v in bfs_order)}")
    
    # Convert to adjacency matrix representation
    print("=== Adjacency Matrix Representation ===")
    adj_matrix = to_adjacency_matrix(graph)
    print(adj_matrix)
    print(f"Matrix shape: {adj_matrix.shape}\n")
    
    # Convert back to adjacency list
    print("=== Adjacency List Representation ===")
    adj_list = to_adjacency_list(graph)
    for vertex, neighbors in adj_list.items():
        print(f"{vertex}: {neighbors}")


if __name__ == "__main__":
    main()
