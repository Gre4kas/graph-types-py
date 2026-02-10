# Graph Types Documentation

This library provides 4 fundamental graph types, each optimized for specific use cases and constraints. All implementations follow SOLID principles and use a custom `GraphRepresentation` strategy for efficient storage.

## 1. SimpleGraph

The most basic graph type. Represents standard mathematical graphs $G = (V, E)$.

**Constraints:**
- No self-loops: An edge cannot connect a vertex to itself.
- No parallel edges: Only one edge can exist between any pair of vertices.
- Can be directed or undirected.

**Usage:**
```python
from packages.graphs.simple_graph import SimpleGraph

# Create undirected simple graph
graph = SimpleGraph(directed=False)
graph.add_vertex("A")
graph.add_vertex("B")
graph.add_edge("A", "B", weight=5.0)

# Check constraints
try:
    graph.add_edge("A", "A")  # Raises GraphConstraintError (self-loop)
except Exception as e:
    print(e)
```

**Implementation Details:**
- Uses `AdjacencyListRepresentation` by default (O(1) average access).
- Supports switching to `AdjacencyMatrixRepresentation` for dense graphs.

---

## 2. Multigraph

Allows multiple edges between the same pair of vertices. Useful for representing complex relationships like multiple flights between cities or multiple transactions between accounts.

**Constraints:**
- **Multiple edges allowed:** Parallel edges are distinct and have unique IDs internally.
- No self-loops allowed.

**Usage:**
```python
from packages.graphs.multigraph import Multigraph

multi = Multigraph()
multi.add_vertex("A")
multi.add_vertex("B")

# Add multiple edges between same vertices
multi.add_edge("A", "B", weight=10.0, label="Day Flight")
multi.add_edge("A", "B", weight=5.0, label="Night Flight")

print(f"Edges between A and B: {multi.edge_multiplicity('A', 'B')}")  # Output: 2
```

**Implementation Details:**
- Uses a specialized `MultigraphRepresentation` where the adjacency list maps to a *list* of neighbors rather than a *set*.

---

## 3. Pseudograph

The most permissive binary graph type. Allows both multiple edges and self-loops.

**Constraints:**
- **Self-loops allowed.**
- **Multiple edges allowed.**

**Usage:**
```python
from packages.graphs.pseudograph import Pseudograph

pseudo = Pseudograph()
pseudo.add_vertex("A")

# Self-loops
pseudo.add_edge("A", "A", weight=1.0)

# Specific methods
print(f"Has self-loop: {pseudo.has_self_loop('A')}")
print(f"Total degree (loop counts x2): {pseudo.total_degree('A')}")
```

**Implementation Details:**
- Inherits mostly from `Multigraph` but relaxes the self-loop constraint check.

---

## 4. Hypergraph

A generalization where an edge (Hyperedge) can connect **any number** of vertices, not just two.

**Constraints:**
- Hyperedges are sets of vertices (size ≥ 1).
- No concept of "direction" in the traditional sense (always undirected).

**Usage:**
```python
from packages.graphs.hypergraph import Hypergraph

hyper = Hypergraph()
hyper.add_vertex("User1")
hyper.add_vertex("User2")
hyper.add_vertex("User3")

# Add a hyperedge representing a group chat
hyper.add_hyperedge({"User1", "User2", "User3"}, label="GroupChat")

# Incidence
print(f"User1 is in hyperedges: {len(hyper.get_incident_hyperedges('User1'))}")
```

**Implementation Details:**
- Uses `HypergraphRepresentation` based on an incidence map.
- Can be converted to a bipartite `SimpleGraph` for visualization or standard algorithm application (nodes + edges become two sets of nodes).

---

## Summary of Differences

| Type | Self-loops? | Multiple Edges? | Edge Arity | Use Case |
|------|-------------|-----------------|------------|----------|
| **SimpleGraph** | ❌ No | ❌ No | 2 | Standard networks, social graphs |
| **Multigraph** | ❌ No | ✅ Yes | 2 | Transport networks, logistics |
| **Pseudograph** | ✅ Yes | ✅ Yes | 2 | State machines, molecular structures |
| **Hypergraph** | N/A | N/A | ≥ 1 | Social groups, biological pathways |
