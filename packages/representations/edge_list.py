"""
Edge list representation for minimal storage.

Optimal for: sparse graphs, serialization, disk storage.
Time Complexity:
- Add vertex: O(1)
- Add edge: O(1)
- Remove vertex: O(E)
- Has edge: O(E) - slow!
- Get neighbors: O(E) - slow!

Space Complexity: O(E)
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from packages.representations.base_representation import GraphRepresentation

if TYPE_CHECKING:
    from collections.abc import Iterator

    from packages.core.edge import Edge
    from packages.core.vertex import Vertex


class EdgeListRepresentation(GraphRepresentation):
    """
    Edge list representation storing edges as a simple list.

    This is the most space-efficient representation but has slow
    neighbor queries. Best for: serialization, export, minimal memory.

    Examples:
        >>> repr = EdgeListRepresentation(directed=False)
        >>> repr.add_vertex(Vertex(id="A"))
        >>> repr.add_edge(Edge(source="A", target="B", weight=5.0))
    """

    __slots__ = ("_vertices", "_edges", "_directed")

    def __init__(self, *, directed: bool = False) -> None:
        """Initialize edge list representation."""
        self._vertices: dict[Any, Vertex] = {}
        self._edges: list[Edge] = []
        self._directed = directed

    def add_vertex(self, vertex: Vertex) -> None:
        """Add vertex. Time: O(1)"""
        if vertex.id in self._vertices:
            msg = f"Vertex {vertex.id!r} already exists"
            raise ValueError(msg)
        self._vertices[vertex.id] = vertex

    def add_edge(self, edge: Edge) -> None:
        """Add edge. Time: O(1)"""
        if edge.source not in self._vertices:
            msg = f"Source vertex {edge.source!r} not found"
            raise KeyError(msg)
        if edge.target not in self._vertices:
            msg = f"Target vertex {edge.target!r} not found"
            raise KeyError(msg)

        # Check for duplicates (slow O(E))
        if self.has_edge(edge.source, edge.target):
            msg = f"Edge {edge.source!r} -> {edge.target!r} already exists"
            raise ValueError(msg)

        self._edges.append(edge)

    def remove_vertex(self, vertex_id: Any) -> None:
        """Remove vertex and incident edges. Time: O(E)"""
        if vertex_id not in self._vertices:
            msg = f"Vertex {vertex_id!r} not found"
            raise KeyError(msg)

        # Remove all incident edges
        self._edges = [
            e for e in self._edges if e.source != vertex_id and e.target != vertex_id
        ]
        del self._vertices[vertex_id]

    def remove_edge(self, source: Any, target: Any) -> None:
        """Remove edge. Time: O(E)"""
        for i, edge in enumerate(self._edges):
            if edge.source == source and edge.target == target:
                del self._edges[i]
                return

        msg = f"Edge {source!r} -> {target!r} not found"
        raise KeyError(msg)

    def has_vertex(self, vertex_id: Any) -> bool:
        """Check vertex exists. Time: O(1)"""
        return vertex_id in self._vertices

    def has_edge(self, source: Any, target: Any) -> bool:
        """Check edge exists. Time: O(E) - SLOW!"""
        for edge in self._edges:
            if edge.source == source and edge.target == target:
                return True
            if not self._directed and edge.source == target and edge.target == source:
                return True
        return False

    def get_neighbors(self, vertex_id: Any) -> set[Any]:
        """Get neighbors. Time: O(E) - SLOW!"""
        if vertex_id not in self._vertices:
            msg = f"Vertex {vertex_id!r} not found"
            raise KeyError(msg)

        neighbors = set()
        for edge in self._edges:
            if edge.source == vertex_id:
                neighbors.add(edge.target)
            elif not self._directed and edge.target == vertex_id:
                neighbors.add(edge.source)
        return neighbors

    def get_vertex(self, vertex_id: Any) -> Vertex:
        """Get vertex. Time: O(1)"""
        if vertex_id not in self._vertices:
            msg = f"Vertex {vertex_id!r} not found"
            raise KeyError(msg)
        return self._vertices[vertex_id]

    def get_edge(self, source: Any, target: Any) -> Edge:
        """Get edge. Time: O(E)"""
        for edge in self._edges:
            if edge.source == source and edge.target == target:
                return edge
        msg = f"Edge {source!r} -> {target!r} not found"
        raise KeyError(msg)

    def vertices(self) -> Iterator[Vertex]:
        """Iterate vertices."""
        yield from self._vertices.values()

    def edges(self) -> Iterator[Edge]:
        """Iterate edges."""
        yield from self._edges

    def vertex_count(self) -> int:
        """Get vertex count."""
        return len(self._vertices)

    def edge_count(self) -> int:
        """Get edge count."""
        return len(self._edges)

    def clear(self) -> None:
        """Clear all data."""
        self._vertices.clear()
        self._edges.clear()

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"EdgeListRepresentation("
            f"vertices={self.vertex_count()}, "
            f"edges={self.edge_count()}, "
            f"directed={self._directed})"
        )
