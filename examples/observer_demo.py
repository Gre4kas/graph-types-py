"""
Demonstration of Observer pattern with EdgeList representation.
"""

from packages.graphs.simple_graph import SimpleGraph
from packages.observers.change_tracker import ChangeLogger, ChangeTracker
from packages.observers.graph_observer import ConsoleObserver


def demo_observers():
    """Demonstrate observers in action."""
    print("=" * 60)
    print("OBSERVER PATTERN DEMONSTRATION")
    print("=" * 60)
    
    # Create graph with multiple observers
    graph = SimpleGraph()
    
    logger = ChangeLogger()
    tracker = ChangeTracker()
    console = ConsoleObserver(prefix="[DEMO]")
    
    graph.attach_observer(logger)
    graph.attach_observer(tracker)
    graph.attach_observer(console)
    
    print("\n1. Adding vertices and edges...")
    graph.add_vertex("A", color="red")
    graph.add_vertex("B", color="blue")
    graph.add_vertex("C", color="green")
    graph.add_edge("A", "B", weight=5.0)
    graph.add_edge("B", "C", weight=3.0)
    graph.add_edge("A", "C", weight=10.0)
    
    print("\n2. Removing edge...")
    graph.remove_edge("A", "C")
    
    print("\n3. Change Logger History:")
    for i, (event, args) in enumerate(logger.get_history(), 1):
        print(f"   {i}. {event}: {args}")
    
    print("\n4. Change Tracker Statistics:")
    stats = tracker.get_statistics()
    for event, count in sorted(stats.items()):
        print(f"   {event}: {count}")
    
    print(f"\n5. Total changes: {tracker.total_changes()}")
    
    print(f"\n6. Most modified vertices:")
    for vertex, count in tracker.get_most_modified_vertices(top_n=3):
        print(f"   {vertex}: {count} changes")


def demo_edge_list():
    """Demonstrate EdgeList representation."""
    print("\n" + "=" * 60)
    print("EDGE LIST REPRESENTATION DEMONSTRATION")
    print("=" * 60)
    
    # Create graph with EdgeList
    graph = SimpleGraph(representation="edge_list")
    
    print("\n1. Creating graph with EdgeList representation...")
    graph.add_vertex("A")
    graph.add_vertex("B")
    graph.add_vertex("C")
    graph.add_edge("A", "B", weight=5.0)
    graph.add_edge("B", "C", weight=3.0)
    
    print(f"   Vertices: {graph.vertex_count()}")
    print(f"   Edges: {graph.edge_count()}")
    
    print("\n2. Export to edge list format:")
    edge_list = graph._representation.to_list()
    for source, target, weight in edge_list:
        print(f"   {source} -- {target} (weight={weight})")
    
    print("\n3. Converting to adjacency list...")
    graph.convert_representation("adjacency_list")
    print(f"   Still has edge A-B: {graph.has_edge('A', 'B')}")
    
    print("\n4. Converting to adjacency matrix...")
    graph.convert_representation("adjacency_matrix")
    print(f"   Still has edge B-C: {graph.has_edge('B', 'C')}")


if __name__ == "__main__":
    demo_observers()
    demo_edge_list()
