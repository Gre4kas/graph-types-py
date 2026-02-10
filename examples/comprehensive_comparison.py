import time
import networkx as nx
from packages.graphs.simple_graph import SimpleGraph
from packages.graphs.multigraph import Multigraph
from packages.graphs.pseudograph import Pseudograph
from packages.graphs.hypergraph import Hypergraph
from packages.algorithms.traversal import bfs
from packages.integrations.networkx_adapter import NetworkXAdapter

def get_incident_edge_degree(graph, vertex_id):
    """Count incident edges (parallel edges count separately, self-loops count twice)."""
    count = 0
    is_directed = getattr(graph, "_directed", False)
    for edge in graph.edges():
        if edge.source == vertex_id:
            count += 1
        if edge.target == vertex_id and (not is_directed or edge.source != edge.target):
            # For undirected, count target matches unless it's a self-loop (already counted)
            # Actually, in undirected graphs, self-loops are usually counted twice
            if not is_directed and edge.source == edge.target:
                count += 1
            elif not is_directed:
                count += 1
    return count

def compare_graph(name, our_graph, nx_graph):
    print(f"\n--- {name} Comparison ---")
    
    # 1. Basic Stats
    our_nodes = our_graph.vertex_count()
    nx_nodes = nx_graph.number_of_nodes()
    
    our_edges = our_graph.edge_count()
    nx_edges = nx_graph.number_of_edges()
    
    print(f"Nodes: Ours={our_nodes}, NX={nx_nodes}")
    print(f"Edges: Ours={our_edges}, NX={nx_edges}")
    
    stats_match = (our_nodes == nx_nodes) and (our_edges == nx_edges)
    print(f"Basic Stats Match: {'✅ YES' if stats_match else '❌ NO'}")

    # 2. Degrees Comparison
    # Note: our_graph.degree() returns unique neighbor count
    # NetworkX .degree() returns incident edge count
    our_unique_neigh = {v.id: our_graph.degree(v.id) for v in our_graph.vertices()}
    our_edge_degree = {v.id: get_incident_edge_degree(our_graph, v.id) for v in our_graph.vertices()}
    nx_degrees = dict(nx_graph.degree())
    
    print(f"Degrees (Ours - Unique Neighbors): {dict(sorted(our_unique_neigh.items()))}")
    print(f"Degrees (Ours - Incident Edges):   {dict(sorted(our_edge_degree.items()))}")
    print(f"Degrees (NetworkX - Incident Edges): {dict(sorted(nx_degrees.items()))}")
    
    match = all(our_edge_degree[k] == nx_degrees[k] for k in our_edge_degree)
    print(f"Structural Degree Match: {'✅ YES' if match else '❌ NO'}")

def run_multigraph_demo():
    multi = Multigraph(directed=False)
    for v in ["A", "B", "C"]: multi.add_vertex(v)
    
    # Add parallel edges
    multi.add_edge("A", "B", weight=2.0)
    multi.add_edge("A", "B", weight=2.0)
    multi.add_edge("B", "C", weight=5.0)
    
    nx_multi = NetworkXAdapter.to_networkx(multi)
    compare_graph("Multigraph", multi, nx_multi)

def run_pseudograph_demo():
    pseudo = Pseudograph(directed=False)
    for v in ["A", "B"]: pseudo.add_vertex(v)
    
    # Self-loops and parallel edges
    pseudo.add_edge("A", "A", weight=2.0)
    pseudo.add_edge("A", "B", weight=1.0)
    pseudo.add_edge("A", "B", weight=5.0)
    
    nx_pseudo = NetworkXAdapter.to_networkx(pseudo)
    compare_graph("Pseudograph", pseudo, nx_pseudo)

def run_hypergraph_demo():
    hyper = Hypergraph()
    for v in ["v1", "v2", "v3", "v4"]: hyper.add_vertex(v)
    
    # Hyperedges: {v1, v2, v3} and {v2, v3, v4}
    hyper.add_hyperedge({"v1", "v2", "v3"}, weight=10.0)
    hyper.add_hyperedge({"v2", "v3", "v4"}, weight=20.0)
    
    # NetworkX adapter will convert Hypergraph to its bipartite representation
    nx_hyper_bipartite = NetworkXAdapter.to_networkx(hyper)
    
    print("\n--- Hypergraph (to Bipartite) Comparison ---")
    # In bipartite representation:
    # Nodes = vertices (4) + hyperedges (2) = 6
    # Edges = incidence count (3 + 3) = 6
    our_nodes = hyper.vertex_count() + hyper.hyperedge_count()
    nx_nodes = nx_hyper_bipartite.number_of_nodes()
    
    incidence_count = sum(len(e.vertices) for e in hyper.edges())
    nx_edges = nx_hyper_bipartite.number_of_edges()
    
    print(f"Bipartite Nodes: Target={our_nodes}, NX={nx_nodes}")
    print(f"Bipartite Edges: Target={incidence_count}, NX={nx_edges}")
    
    match = (our_nodes == nx_nodes) and (incidence_count == nx_edges)
    print(f"Hypergraph Structure Match: {'✅ YES' if match else '❌ NO'}")

if __name__ == "__main__":
    print("=== Comprehensive Graph Library vs NetworkX Comparison ===")
    run_multigraph_demo()
    run_pseudograph_demo()
    run_hypergraph_demo()
