"""
Demonstration of graph serialization capabilities.
"""

from pathlib import Path

from packages.graphs.simple_graph import SimpleGraph
from packages.utils.serializers import (
    GraphIO,
    JSONSerializer,
    PickleSerializer,
    load_graph,
    save_graph,
)


def demo_json_serialization():
    """Demonstrate JSON serialization."""
    print("=" * 60)
    print("JSON SERIALIZATION DEMO")
    print("=" * 60)

    # Create sample graph
    graph = SimpleGraph()
    graph.add_vertex("London", country="UK", population=9_000_000)
    graph.add_vertex("Paris", country="France", population=2_200_000)
    graph.add_vertex("Berlin", country="Germany", population=3_700_000)
    graph.add_edge("London", "Paris", weight=344.0, transport="train")
    graph.add_edge("Paris", "Berlin", weight=878.0, transport="train")

    print("\n1. Original graph:")
    print(f"   Vertices: {graph.vertex_count()}")
    print(f"   Edges: {graph.edge_count()}")

    # Save to JSON
    json_path = Path("temp_graph.json")
    JSONSerializer.save(graph, json_path, indent=2)
    print(f"\n2. Saved to: {json_path}")
    print(f"   File size: {json_path.stat().st_size} bytes")

    # Show JSON content (first 500 chars)
    with json_path.open("r") as f:
        content = f.read()
    print(f"\n3. JSON content preview:")
    print("   " + content[:500] + "...")

    # Load from JSON
    loaded = JSONSerializer.load(json_path)
    print(f"\n4. Loaded from JSON:")
    print(f"   Vertices: {loaded.vertex_count()}")
    print(f"   Edges: {loaded.edge_count()}")
    print(f"   Has London: {loaded.has_vertex('London')}")
    print(f"   Has edge London-Paris: {loaded.has_edge('London', 'Paris')}")

    # Verify attributes preserved
    london = loaded.get_vertex("London")
    print(f"\n5. Attributes preserved:")
    print(f"   London population: {london.attributes['population']:,}")
    print(f"   London country: {london.attributes['country']}")

    # Cleanup
    json_path.unlink()


def demo_pickle_serialization():
    """Demonstrate Pickle serialization."""
    print("\n" + "=" * 60)
    print("PICKLE SERIALIZATION DEMO")
    print("=" * 60)

    # Create graph with complex data
    graph = SimpleGraph()
    graph.add_vertex(
        "Node1",
        data=[1, 2, 3, 4, 5],
        metadata={"type": "important", "tags": ["primary", "active"]},
    )
    graph.add_vertex(
        "Node2",
        data=[6, 7, 8],
        metadata={"type": "secondary", "tags": ["backup"]},
    )
    graph.add_edge("Node1", "Node2", weight=100.0, info={"bidirectional": True})

    print("\n1. Original graph with complex attributes:")
    print(f"   Vertices: {graph.vertex_count()}")
    node1 = graph.get_vertex("Node1")
    print(f"   Node1 data: {node1.attributes['data']}")
    print(f"   Node1 tags: {node1.attributes['metadata']['tags']}")

    # Save to Pickle
    pickle_path = Path("temp_graph.pkl")
    PickleSerializer.save(graph, pickle_path)
    print(f"\n2. Saved to: {pickle_path}")
    print(f"   File size: {pickle_path.stat().st_size} bytes")

    # Load from Pickle
    loaded = PickleSerializer.load(pickle_path)
    print(f"\n3. Loaded from Pickle:")
    print(f"   Vertices: {loaded.vertex_count()}")

    # Verify complex attributes
    loaded_node1 = loaded.get_vertex("Node1")
    print(f"\n4. Complex attributes preserved:")
    print(f"   Data list: {loaded_node1.attributes['data']}")
    print(f"   Nested dict: {loaded_node1.attributes['metadata']}")

    # Cleanup
    pickle_path.unlink()


def demo_graphio_interface():
    """Demonstrate GraphIO convenience interface."""
    print("\n" + "=" * 60)
    print("GRAPHIO CONVENIENCE INTERFACE DEMO")
    print("=" * 60)

    graph = SimpleGraph()
    graph.add_vertex("A")
    graph.add_vertex("B")
    graph.add_vertex("C")
    graph.add_edge("A", "B", weight=1.0)
    graph.add_edge("B", "C", weight=2.0)

    print("\n1. Using GraphIO.save() - auto-detects format:")

    # Save as JSON (detected from extension)
    json_file = Path("auto.json")
    GraphIO.save(graph, json_file)
    print(f"   Saved as JSON: {json_file}")

    # Save as Pickle (detected from extension)
    pkl_file = Path("auto.pkl")
    GraphIO.save(graph, pkl_file)
    print(f"   Saved as Pickle: {pkl_file}")

    print("\n2. Using GraphIO.load() - auto-detects format:")

    # Load JSON
    from_json = GraphIO.load(json_file)
    print(f"   Loaded from JSON: {from_json.vertex_count()} vertices")

    # Load Pickle
    from_pickle = GraphIO.load(pkl_file)
    print(f"   Loaded from Pickle: {from_pickle.vertex_count()} vertices")

    print("\n3. Using convenience functions:")

    # Module-level functions
    save_graph(graph, "convenient.json")
    loaded = load_graph("convenient.json")
    print(f"   save_graph/load_graph: {loaded.vertex_count()} vertices")

    # Cleanup
    json_file.unlink()
    pkl_file.unlink()
    Path("convenient.json").unlink()


def demo_format_comparison():
    """Compare JSON vs Pickle formats."""
    print("\n" + "=" * 60)
    print("FORMAT COMPARISON: JSON vs PICKLE")
    print("=" * 60)

    # Create medium-sized graph
    graph = SimpleGraph()
    for i in range(100):
        graph.add_vertex(i, index=i, label=f"Node_{i}")

    for i in range(150):
        source = i % 100
        target = (i + 1) % 100
        if not graph.has_edge(source, target):
            graph.add_edge(source, target, weight=float(i))

    print(f"\nGraph: {graph.vertex_count()} vertices, {graph.edge_count()} edges")

    # Save in both formats
    json_path = Path("comparison.json")
    pickle_path = Path("comparison.pkl")

    JSONSerializer.save(graph, json_path)
    PickleSerializer.save(graph, pickle_path)

    json_size = json_path.stat().st_size
    pickle_size = pickle_path.stat().st_size

    print(f"\nFile sizes:")
    print(f"   JSON:   {json_size:,} bytes")
    print(f"   Pickle: {pickle_size:,} bytes")
    print(f"   Ratio:  {json_size / pickle_size:.2f}x")

    print(f"\nJSON is human-readable:")
    with json_path.open("r") as f:
        print(f"   First 200 chars: {f.read(200)}")

    print(f"\nPickle is binary:")
    with pickle_path.open("rb") as f:
        print(f"   First 50 bytes: {f.read(50)}")

    # Cleanup
    json_path.unlink()
    pickle_path.unlink()


if __name__ == "__main__":
    demo_json_serialization()
    demo_pickle_serialization()
    demo_graphio_interface()
    demo_format_comparison()

    print("\n" + "=" * 60)
    print("✅ ALL SERIALIZATION DEMOS COMPLETED!")
    print("=" * 60)
