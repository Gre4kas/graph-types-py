"""Edge list representation for minimal storage.

Optimal for: sparse graphs, serialization, disk storage, export/import.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Iterable

from packages.representations.base_representation import GraphRepresentation

if TYPE_CHECKING:
    from collections.abc import Iterator

    from packages.core.edge import Edge
    from packages.core.vertex import Vertex


class EdgeListRepresentation(GraphRepresentation):
    """
    Edge list representation storing edges as a simple list.
    """

    __slots__ = ("_vertices", "_edges", "_directed")

    def __init__(self, *, directed: bool = False) -> None:
        self._vertices: dict[Any, Vertex] = {}
        self._edges: list[Edge] = []
        self._directed = directed

    def add_vertex(self, vertex: Vertex) -> None:
        if vertex.id in self._vertices:
            return # Idempotent
        self._vertices[vertex.id] = vertex

    def remove_vertex(self, vertex_id: Any) -> None:
        if vertex_id not in self._vertices:
            msg = f"Vertex {vertex_id!r} not found"
            raise KeyError(msg)

        self._edges = [
            e for e in self._edges 
            if e.source != vertex_id and e.target != vertex_id
        ]
        del self._vertices[vertex_id]

    def add_edge(self, edge: Edge) -> None:
        if edge.source not in self._vertices:
            msg = f"Source vertex {edge.source!r} not found"
            raise ValueError(msg) # Changed to ValueError
        if edge.target not in self._vertices:
            msg = f"Target vertex {edge.target!r} not found"
            raise ValueError(msg)

        if self.has_edge(edge.source, edge.target):
            msg = f"Edge {edge.source!r} -> {edge.target!r} already exists"
            raise ValueError(msg)

        self._edges.append(edge)

    def remove_edge(self, source: Any, target: Any) -> None:
        for i, edge in enumerate(self._edges):
            if edge.source == source and edge.target == target:
                del self._edges[i]
                return
            if not self._directed and edge.source == target and edge.target == source:
                del self._edges[i]
                return
        msg = f"Edge {source!r} -> {target!r} not found"
        raise ValueError(msg) # Changed to ValueError

    def has_edge(self, source: Any, target: Any) -> bool:
        for edge in self._edges:
            if edge.source == source and edge.target == target:
                return True
            if not self._directed and edge.source == target and edge.target == source:
                return True
        return False

    def get_edge(self, source: Any, target: Any) -> Edge:
        for edge in self._edges:
            if edge.source == source and edge.target == target:
                return edge
            if not self._directed and edge.source == target and edge.target == source:
                return edge
        msg = f"Edge {source!r} -> {target!r} not found"
        raise ValueError(msg)

    def get_all_edges(self, source: Any, target: Any) -> list[Edge]:
        try:
            return [self.get_edge(source, target)]
        except ValueError:
            return []

    def get_neighbors(self, vertex_id: Any) -> Iterable[Any]:
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

    def vertex_count(self) -> int:
        return len(self._vertices)

    def edge_count(self) -> int:
        return len(self._edges)

    # Legacy / extra methods
    def to_list(self) -> list[tuple[Any, Any, float]]:
        return [(e.source, e.target, e.weight) for e in self._edges]
    
    def clear(self) -> None:
        self._vertices.clear()
        self._edges.clear()
