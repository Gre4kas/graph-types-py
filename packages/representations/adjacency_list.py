"""Adjacency list representation for sparse graphs.

This module implements the adjacency list representation using dictionaries
and sets for O(1) average-case operations. Optimal for sparse graphs where
|E| << |V|².
"""

from __future__ import annotations

from collections import defaultdict
from typing import TYPE_CHECKING, Any, Iterable

from packages.representations.base_representation import GraphRepresentation

if TYPE_CHECKING:
    from collections.abc import Iterator

    from packages.core.edge import Edge
    from packages.core.vertex import Vertex


class AdjacencyListRepresentation(GraphRepresentation):
    """
    Adjacency list representation using dict[vertex_id, set[vertex_id]].

    This is the default representation for most graph types, providing
    excellent performance for sparse graphs and dynamic modifications.

    Attributes:
        _adj_list: Adjacency dictionary mapping vertex_id -> set of neighbor_ids
        _vertices: Dictionary mapping vertex_id -> Vertex object
        _edges: Dictionary mapping (source, target) -> Edge object
        _directed: Whether the graph is directed
    """

    __slots__ = ("_adj_list", "_vertices", "_edges", "_directed")

    def __init__(self, *, directed: bool = False) -> None:
        """
        Initialize adjacency list representation.

        Args:
            directed: Whether the graph is directed
        """
        self._adj_list: dict[Any, set[Any]] = defaultdict(set)
        self._vertices: dict[Any, Vertex] = {}
        self._edges: dict[tuple[Any, Any], Edge] = {}
        self._directed = directed

    def add_vertex(self, vertex: Vertex) -> None:
        if vertex.id in self._vertices:
            # Idempotent behavior for new contract
            return
        self._vertices[vertex.id] = vertex
        self._adj_list[vertex.id]  # Initialize empty set

    def remove_vertex(self, vertex_id: Any) -> None:
        if vertex_id not in self._vertices:
            msg = f"Vertex {vertex_id!r} not found"
            raise KeyError(msg)

        neighbors = list(self._adj_list[vertex_id])
        for neighbor in neighbors:
            self._adj_list[neighbor].discard(vertex_id)
            self._edges.pop((vertex_id, neighbor), None)
            self._edges.pop((neighbor, vertex_id), None)

        del self._vertices[vertex_id]
        del self._adj_list[vertex_id]

        edges_to_remove = [
            key for key in self._edges if key[0] == vertex_id or key[1] == vertex_id
        ]
        for key in edges_to_remove:
            del self._edges[key]

    def add_edge(self, edge: Edge) -> None:
        if edge.source not in self._vertices:
            msg = f"Source vertex {edge.source!r} not found"
            raise ValueError(msg)
        if edge.target not in self._vertices:
            msg = f"Target vertex {edge.target!r} not found"
            raise ValueError(msg)

        edge_key = (edge.source, edge.target)
        # For legacy reasons, we might want to allow updating?
        # But new contract says raises error for simple graphs
        # We'll allow overwrite or ignore for now to pass tests or raise if strictly simple
        # The old code raised ValueError.
        if edge_key in self._edges:
             msg = f"Edge {edge.source!r} -> {edge.target!r} already exists"
             raise ValueError(msg)

        self._adj_list[edge.source].add(edge.target)
        if not self._directed:
            self._adj_list[edge.target].add(edge.source)

        self._edges[edge_key] = edge
        if not self._directed:
            self._edges[(edge.target, edge.source)] = edge

    def remove_edge(self, source: Any, target: Any) -> None:
        edge_key = (source, target)
        if edge_key not in self._edges:
            msg = f"Edge {source!r} -> {target!r} not found"
            raise ValueError(msg)

        self._adj_list[source].discard(target)
        if not self._directed:
            self._adj_list[target].discard(source)

        del self._edges[edge_key]
        if not self._directed:
            self._edges.pop((target, source), None)

    def has_edge(self, source: Any, target: Any) -> bool:
        return (source, target) in self._edges

    def get_edge(self, source: Any, target: Any) -> Edge:
        edge_key = (source, target)
        if edge_key not in self._edges:
            msg = f"Edge {source!r} -> {target!r} not found"
            raise ValueError(msg)
        return self._edges[edge_key]

    def get_all_edges(self, source: Any, target: Any) -> list[Edge]:
        """Retrieve all edges between two vertices."""
        try:
            return [self.get_edge(source, target)]
        except ValueError:
            return []

    def get_neighbors(self, vertex_id: Any) -> Iterable[Any]:
        if vertex_id not in self._vertices:
            msg = f"Vertex {vertex_id!r} not found"
            raise KeyError(msg)
        return self._adj_list[vertex_id]

    def vertex_count(self) -> int:
        return len(self._vertices)

    def edge_count(self) -> int:
        if self._directed:
            return len(self._edges)
        return len(self._edges) // 2

    # Legacy methods for compatibility
    def has_vertex(self, vertex_id: Any) -> bool:
        return vertex_id in self._vertices
    
    def get_vertex(self, vertex_id: Any) -> Vertex:
        if vertex_id not in self._vertices:
            raise KeyError(f"Vertex {vertex_id} not found")
        return self._vertices[vertex_id]

    def clear(self) -> None:
        self._adj_list.clear()
        self._vertices.clear()
        self._edges.clear()

    @property
    def directed(self) -> bool:
        return self._directed
