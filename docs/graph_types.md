# Graph Types: Comprehensive Guide

Choosing the right graph representation is the first step in successful modeling. This library provides four distinct types to cover all mathematical and practical needs.

---

## 🧭 How to Choose the Right Graph

Use this matrix to determine which class fits your project best:

| Constraint | SimpleGraph | Multigraph | Pseudograph | Hypergraph |
| :--- | :---: | :---: | :---: | :---: |
| **Self-loops** (A → A) | ❌ No | ❌ No | ✅ Yes | N/A |
| **Parallel Edges** (A ⇉ B) | ❌ No | ✅ Yes | ✅ Yes | ✅ Yes |
| **Arity** (Nodes per edge) | Exactly 2 | Exactly 2 | Exactly 2 | Any (2, 3+) |
| **Default Internal Repr** | Adjacency List | Multi-List | Multi-List | Incidence Map |

---

## 1. SimpleGraph
*Standard mathematical graph: $G = (V, E)$.*

### 🛠️ Architecture
The `SimpleGraph` is optimized for speed and mathematical purity. It strictly enforces that no vertex connects to itself and no two vertices share more than one edge.

### 🚀 Usage Guide
```python
from packages.graphs import SimpleGraph

# 1. Initialization
# representation can be: "adjacency_list" (default) or "adjacency_matrix"
graph = SimpleGraph(directed=False, representation="adjacency_list")

# 2. Vertex Management
graph.add_vertex("Kyiv", population=2800000)
graph.add_vertex("Lviv", region="West")

# 3. Edge Management
graph.add_edge("Kyiv", "Lviv", weight=540) # O(1) avg

# 4. Constraints (Safety)
try:
    graph.add_edge("Kyiv", "Kyiv") # Raises GraphConstraintError
except:
    print("Self-loops are forbidden in SimpleGraph!")
```

---

## 2. Multigraph
*Relationship focus: Multiple connections between points.*

### 🛠️ Architecture
A `Multigraph` allows parallel edges. Each edge is assigned a unique internal ID, allowing you to store different attributes for each connection between the same nodes.

### 🌟 Unique Methods
- `edge_multiplicity(u, v)`: Returns the count of edges between `u` and `v`.
- `get_edges_between(u, v)`: Returns a list of `Edge` objects.

### 🚀 Usage Guide
```python
from packages.graphs import Multigraph

multi = Multigraph()
multi.add_vertex("Account1")
multi.add_vertex("Account2")

# Multiple transactions between same accounts
multi.add_edge("Account1", "Account2", amount=100, date="2024-01-01")
multi.add_edge("Account1", "Account2", amount=250, date="2024-01-02")

print(f"Transactions: {multi.edge_multiplicity('Account1', 'Account2')}") # Output: 2
```

---

## 3. Pseudograph
*Topology focus: Circular references and complex states.*

### 🛠️ Architecture
The `Pseudograph` is the most flexible choice for binary edges. It inherits from `Multigraph` but relaxes the constraint on self-loops.

### 🌟 Unique Methods
- `has_self_loop(v)`: Boolean check for specific vertex.
- `count_self_loops()`: Total count in graph.
- `total_degree(v)`: Calculates degree where self-loops count as **2**.

### 🚀 Usage Guide
```python
from packages.graphs import Pseudograph

pseudo = Pseudograph()
pseudo.add_vertex("Process_A")

# Maintenance state: process points to itself
pseudo.add_edge("Process_A", "Process_A", status="stabilizing")

print(pseudo.total_degree("Process_A")) # Output: 2 (correct graph theory behavior)
```

---

## 4. Hypergraph
*Set focus: Group collaborations and high-order relations.*

### 🛠️ Architecture
In a `Hypergraph`, edges aren't pairs; they are sets. Use this when a "connection" involves 3 or more entities simultaneously (e.g., a group chat, a molecule, or a technical committee).

### 🌟 Unique Methods
- `add_hyperedge({"A", "B", "C"})`: Create multi-vertex connection.
- `get_incident_hyperedges(v)`: Find all "groups" a vertex belongs to.
- `to_bipartite_graph()`: Convert to a `SimpleGraph` for visualization.

### 🚀 Usage Guide
```python
from packages.graphs import Hypergraph

hyper = Hypergraph()
users = ["Alice", "Bob", "Charlie", "David"]
for u in users: hyper.add_vertex(u)

# Create a project team including 3 users
hyper.add_hyperedge({"Alice", "Bob", "Charlie"}, project="AI_Model")

# Alice is in which projects?
projects = hyper.get_incident_hyperedges("Alice")
```
