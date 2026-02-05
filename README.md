# Graph Library

Professional Python library for working with all mathematical graph types.

## Features

- ✅ **All graph types**: Simple, Multigraph, Pseudograph, Hypergraph
- ✅ **Multiple representations**: Adjacency list, matrix, edge list
- ✅ **Rich algorithms**: BFS, DFS, Dijkstra, Bellman-Ford, connectivity
- ✅ **Type-safe**: Full type hints with Python 3.12+
- ✅ **Validated**: Pydantic v2 for data integrity
- ✅ **Tested**: >90% coverage with pytest
- ✅ **Fast**: NumPy-optimized, graph-tool integration ready

## Installation

```bash
# Using UV (recommended for 2025-2026)
uv pip install graph-library

# Using pip
pip install graph-library

### Serialization

Save and load graphs in JSON or Pickle formats:

```python
from packages.graphs.simple_graph import SimpleGraph
from packages.utils.serializers import GraphIO, JSONSerializer, PickleSerializer

# Create graph
graph = SimpleGraph()
graph.add_vertex("A", priority=1)
graph.add_edge("A", "B", weight=5.0)

# JSON format (human-readable)
JSONSerializer.save(graph, "graph.json")
loaded = JSONSerializer.load("graph.json")

# Pickle format (binary, faster)
PickleSerializer.save(graph, "graph.pkl")
loaded = PickleSerializer.load("graph.pkl")

# Auto-detect format from extension
GraphIO.save(graph, "graph.json")  # Uses JSON
GraphIO.save(graph, "graph.pkl")   # Uses Pickle
loaded = GraphIO.load("graph.json")

# Convenience functions
from packages.utils.serializers import save_graph, load_graph
save_graph(graph, "output.json")
graph = load_graph("output.json")
