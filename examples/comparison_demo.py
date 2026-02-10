import time
import networkx as nx
from packages.graphs.simple_graph import SimpleGraph
from packages.algorithms.shortest_path import dijkstra
from packages.integrations.networkx_adapter import NetworkXAdapter

def run_comparison():
    print("=== Graph Library vs NetworkX Comparison ===")
    
    # 1. Create a sample graph in our library
    graph = SimpleGraph(directed=False)
    vertices = ["A", "B", "C", "D", "E", "F", "G"]
    for v in vertices:
        graph.add_vertex(v)
    
    edges = [
        ("A", "B", 4.0), ("A", "C", 3.0),
        ("B", "D", 2.0), ("B", "E", 3.0),
        ("C", "E", 1.0), ("C", "F", 6.0),
        ("D", "G", 5.0), ("E", "G", 2.0),
        ("F", "G", 1.0)
    ]
    for u, v, w in edges:
        graph.add_edge(u, v, weight=w)

    print(f"Created graph with {graph.vertex_count()} vertices and {graph.edge_count()} edges.")

    # 2. Convert to NetworkX for comparison
    nx_graph = NetworkXAdapter.to_networkx(graph)

    # 3. Benchmark Custom Dijkstra
    start_time = time.perf_counter()
    # Run multiple times for better measurement
    for _ in range(100):
        custom_distances = dijkstra(graph, "A")
    custom_duration = (time.perf_counter() - start_time) / 100
    
    # 4. Benchmark NetworkX Dijkstra
    start_time = time.perf_counter()
    for _ in range(100):
        nx_distances = nx.single_source_dijkstra_path_length(nx_graph, "A")
    nx_duration = (time.perf_counter() - start_time) / 100

    # 5. Compare Results
    print("\n--- Results Correctness ---")
    custom_sorted = {k: custom_distances[k] for k in sorted(custom_distances)}
    nx_sorted = {k: nx_distances[k] for k in sorted(nx_distances)}
    
    print(f"Custom Dijkstra:  {custom_sorted}")
    print(f"NetworkX Dijkstra: {nx_sorted}")
    
    results_match = all(custom_distances[v] == nx_distances[v] for v in custom_distances)
    print(f"Results Match: {'✅ YES' if results_match else '❌ NO'}")

    # 6. Compare Timing
    print("\n--- Performance Timing (Average over 100 runs) ---")
    print(f"Custom Implementation: {custom_duration*1000:0.4f} ms")
    print(f"NetworkX (Native):     {nx_duration*1000:0.4f} ms")
    
    ratio = custom_duration / nx_duration
    print(f"Speed Ratio: {ratio:0.2f}x (lower is faster for custom)")

if __name__ == "__main__":
    run_comparison()
