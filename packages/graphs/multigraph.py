"""
Multigraph implementation (multiple edges, no loops).

Mathematical definition: Multigraph allows multiple edges between the same
pair of vertices but prohibits self-loops.
"""

from __future__ import annotations

from collections import defaultdict
from typing import TYPE_CHECKING, Any

from packages.core.base_graph import BaseGraph
from packages.core.edge import Edge
from packages.core.vertex import Vertex
from packages.representations.base_representation import GraphRepresentation
from packages.utils.exceptions import GraphConstraintError, VertexNotFoundError

if TYPE_CHECKING:
    from collections.abc import Iterator


class MultigraphRepresentation(GraphRepresentation):
    """
    Specialized representation for multigraphs allowing parallel edges.

    Stores edges as lists to allow multiple edges between same vertices.
    """

    __slots__ = ("_adj_list", "_vertices", "_edges", "_directed", "_edge_counter")

    def __init__(self, *, directed: bool = False) -> None:
        """Initialize multigraph representation."""
        self._adj_list: dict[Any, list[Any]] = defaultdict(list)
        self._vertices: dict[Any, Vertex] = {}
        self._edges: dict[int, Edge] = {}  # edge_id -> Edge
        self._directed = directed
        self._edge_counter = 0

    def add_vertex(self, vertex: Vertex) -> None:
        """Add vertex to multigraph."""
        if vertex.id in self._vertices:
            msg = f"Vertex {vertex.id!r} already exists"
            raise ValueError(msg)
        self._vertices[vertex.id] = vertex
        self._adj_list[vertex.id]

    def add_edge(self, edge: Edge) -> int:
        """
        Add edge to multigraph and return edge ID.

        Unlike simple graphs, multiple edges between same vertices are allowed.

        Returns:
            Unique edge identifier
        """
        if edge.source not in self._vertices:
            msg = f"Source vertex {edge.source!r} not found"
            raise KeyError(msg)
        if edge.target not in self._vertices:
            msg = f"Target vertex {edge.target!r} not found"
            raise KeyError(msg)

        # Assign unique edge ID
        edge_id = self._edge_counter
        self._edge_counter += 1

        # Add to adjacency list
        self._adj_list[edge.source].append(edge.target)
        if not self._directed:
            self._adj_list[edge.target].append(edge.source)

        # Store edge with ID
        self._edges[edge_id] = edge

        return edge_id

    def remove_vertex(self, vertex_id: Any) -> None:
        """Remove vertex and all incident edges."""
        if vertex_id not in self._vertices:
            msg = f"Vertex {vertex_id!r} not found"
            raise KeyError(msg)

        # Remove all edges involving this vertex
        edges_to_remove = [
            eid for eid, e in self._edges.items() if e.source == vertex_id or e.target == vertex_id
        ]
        for eid in edges_to_remove:
            del self._edges[eid]

        # Remove from adjacency list
        del self._adj_list[vertex_id]
        for neighbors in self._adj_list.values():
            while vertex_id in neighbors:
                neighbors.remove(vertex_id)

        # Remove vertex
        del self._vertices[vertex_id]

    def remove_edge(self, source: Any, target: Any) -> None:
        """
        Remove one edge between source and target.

        If multiple edges exist, removes the first one found.
        """
        # Find first matching edge
        edge_id = None
        for eid, edge in self._edges.items():
            if edge.source == source and edge.target == target:
                edge_id = eid
                break

        if edge_id is None:
            msg = f"Edge {source!r} -> {target!r} not found"
            raise KeyError(msg)

        # Remove from adjacency list
        self._adj_list[source].remove(target)
        if not self._directed:
            self._adj_list[target].remove(source)

        # Remove edge
        del self._edges[edge_id]

    def has_vertex(self, vertex_id: Any) -> bool:
        """Check if vertex exists."""
        return vertex_id in self._vertices

    def has_edge(self, source: Any, target: Any) -> bool:
        """Check if at least one edge exists between source and target."""
        return target in self._adj_list.get(source, [])

    def get_neighbors(self, vertex_id: Any) -> set[Any]:
        """Get unique neighbors (may have multiple edges to same neighbor)."""
        if vertex_id not in self._vertices:
            msg = f"Vertex {vertex_id!r} not found"
            raise KeyError(msg)
        return set(self._adj_list[vertex_id])

    def get_vertex(self, vertex_id: Any) -> Vertex:
        """Get vertex object."""
        if vertex_id not in self._vertices:
            msg = f"Vertex {vertex_id!r} not found"
            raise KeyError(msg)
        return self._vertices[vertex_id]

    def get_edge(self, source: Any, target: Any) -> Edge:
        """Get first edge between source and target."""
        for edge in self._edges.values():
            if edge.source == source and edge.target == target:
                return edge
        msg = f"Edge {source!r} -> {target!r} not found"
        raise KeyError(msg)

    def vertices(self) -> Iterator[Vertex]:
        """Iterate over vertices."""
        yield from self._vertices.values()

    def edges(self) -> Iterator[Edge]:
        """Iterate over all edges (including parallel edges)."""
        yield from self._edges.values()

    def vertex_count(self) -> int:
        """Get vertex count."""
        return len(self._vertices)

    def edge_count(self) -> int:
        """Get edge count (including parallel edges)."""
        return len(self._edges)

    def clear(self) -> None:
        """Clear all data."""
        self._adj_list.clear()
        self._vertices.clear()
        self._edges.clear()
        self._edge_counter = 0


class Multigraph(BaseGraph[Any, Any]):
    """
    Multigraph: allows multiple edges between vertices, no self-loops.

    Examples:
        >>> multi = Multigraph()
        >>> multi.add_vertex("A")
        >>> multi.add_vertex("B")
        >>> multi.add_edge("A", "B", weight=3.0)
        >>> multi.add_edge("A", "B", weight=5.0)  # Allowed (parallel edge)
        >>> multi.edge_count()
        2
        >>> multi.add_edge("A", "A")  # Raises GraphConstraintError
    """

    def _create_representation(self, repr_type: str) -> GraphRepresentation:
        """Create multigraph representation."""
        if repr_type != "adjacency_list":
            msg = "Multigraph currently only supports adjacency_list representation"
            raise ValueError(msg)
        return MultigraphRepresentation(directed=self._directed)

    def add_vertex(self, vertex_id: Any, **attributes: Any) -> None:
        """Add vertex to multigraph."""
        vertex = Vertex(id=vertex_id, attributes=attributes)
        self._representation.add_vertex(vertex)
        self._notify_observers("vertex_added", vertex_id)

    def add_edge(
        self,
        source: Any,
        target: Any,
        *,
        weight: float = 1.0,
        **attributes: Any,
    ) -> None:
        """
        Add edge to multigraph.

        Multiple edges between same vertices are allowed.
        Self-loops are prohibited.
        """
        # Constraint: No self-loops
        if source == target:
            msg = f"Multigraphs cannot contain self-loops: {source!r}"
            raise GraphConstraintError(msg)

        edge = Edge(
            source=source,
            target=target,
            weight=weight,
            directed=self._directed,
            attributes=attributes,
        )
        self._representation.add_edge(edge)
        self._notify_observers("edge_added", source, target)

    def remove_vertex(self, vertex_id: Any) -> None:
        """Remove vertex from multigraph."""
        self._representation.remove_vertex(vertex_id)
        self._notify_observers("vertex_removed", vertex_id)

    def remove_edge(self, source: Any, target: Any) -> None:
        """Remove one edge between vertices (if multiple exist, removes first)."""
        self._representation.remove_edge(source, target)
        self._notify_observers("edge_removed", source, target)

    def has_vertex(self, vertex_id: Any) -> bool:
        """Check if vertex exists."""
        return self._representation.has_vertex(vertex_id)

    def has_edge(self, source: Any, target: Any) -> bool:
        """Check if at least one edge exists."""
        return self._representation.has_edge(source, target)

    def get_neighbors(self, vertex_id: Any) -> set[Any]:
        """Get neighbors (unique, even if multiple edges exist)."""
        return self._representation.get_neighbors(vertex_id)

    def vertex_count(self) -> int:
        """Get total number of vertices."""
        return self._representation.vertex_count()

    def edge_count(self) -> int:
        """Get total number of edges (including parallel edges)."""
        return self._representation.edge_count()

    def vertices(self) -> Iterator[Vertex]:
        """Iterate over vertices."""
        yield from self._representation.vertices()

    def edges(self) -> Iterator[Edge]:
        """Iterate over all edges (including parallel edges)."""
        yield from self._representation.edges()

    def edge_multiplicity(self, source: Any, target: Any) -> int:
        """
        Get number of edges between two vertices.

        Returns:
            Number of parallel edges
        """
        count = 0
        for edge in self.edges():
            if edge.source == source and edge.target == target:
                count += 1
        return count
