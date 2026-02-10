"""
Multigraph Example for graph-types-py

Demonstrates:
- Creating a multigraph (multiple edges between same vertices)
- Modeling multiple transportation routes between cities
- DFS traversal algorithm
- Working with parallel edges (multiple connections)
"""

from packages.graphs import Multigraph
from packages.algorithms.traversal import dfs
from packages.representations.edge_list import to_edge_list


def main():
    # Create a multigraph representing multiple transportation routes
    graph = Multigraph(directed=False)
    
    # Add vertices (cities)
    cities = ["Kyiv", "Lviv", "Odesa", "Kharkiv", "Dnipro"]
    for city in cities:
        graph.add_vertex(city)
    
    # Add multiple edges between same vertices (different transport types)
    # Format: (source, target, weight, transport_type)
    routes = [
        ("Kyiv", "Lviv", 540, "highway"),
        ("Kyiv", "Lviv", 600, "railway"),
        ("Kyiv", "Lviv", 700, "scenic_route"),
        ("Kyiv", "Kharkiv", 480, "highway"),
        ("Kyiv", "Kharkiv", 520, "railway"),
        ("Kharkiv", "Dnipro", 220, "highway"),
        ("Kyiv", "Odesa", 475, "highway"),
        ("Kyiv", "Odesa", 500, "railway"),
        ("Lviv", "Odesa", 790, "highway"),
    ]
    
    for source, target, weight, transport in routes:
        graph.add_edge(source, target, weight=weight, transport_type=transport)
    
    print("=== Multigraph Structure ===")
    print(f"Vertices: {graph.get_vertices()}")
    print(f"Total edges (including parallel edges): {graph.edge_count()}")
    
    # Show parallel edges between Kyiv and Lviv
    parallel_edges = graph.get_edges_between("Kyiv", "Lviv")
    print(f"\nParallel edges between Kyiv and Lviv:")
    for edge in parallel_edges:
        print(f"  - {edge['transport_type']}: {edge['weight']} km")
    
    # Perform DFS traversal starting from Kyiv
    print("\n=== DFS Traversal from Kyiv ===")
    dfs_order = list(dfs(graph, "Kyiv"))
    print(f"Order: {' -> '.join(str(v) for v in dfs_order)}")
    
    # Convert to edge list representation (shows all parallel edges)
    print("=== Edge List Representation ===")
    edge_list = to_edge_list(graph)
    for i, edge in enumerate(edge_list, 1):
        print(f"{i}. {edge['source']} -- {edge['target']} "
              f"[{edge.get('transport_type', 'unknown')}]: {edge['weight']} km")


if __name__ == "__main__":
    main()
