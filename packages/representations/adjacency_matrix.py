"""Adjacency matrix representation for dense graphs.

This module implements the adjacency matrix representation using NumPy arrays
for O(1) edge lookups and efficient matrix operations.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Iterable

import numpy as np

from packages.representations.base_representation import GraphRepresentation

if TYPE_CHECKING:
    from collections.abc import Iterator

    from packages.core.edge import Edge
    from packages.core.vertex import Vertex


class AdjacencyMatrixRepresentation(GraphRepresentation):
    """Adjacency matrix representation using NumPy 2D array."""

    __slots__ = (
        "_matrix",
        "_vertices",
        "_vertex_index",
        "_index_vertex",
        "_edges",
        "_directed",
    )

    def __init__(
        self,
        *,
        directed: bool = False,
        initial_capacity: int = 10,
    ) -> None:
        """Initialize adjacency matrix representation."""
        self._matrix = np.zeros((initial_capacity, initial_capacity), dtype=np.float64)
        self._vertices: dict[Any, Vertex] = {}
        self._vertex_index: dict[Any, int] = {}
        self._index_vertex: list[Any] = []
        self._edges: dict[tuple[Any, Any], Edge] = {}
        self._directed = directed

    def _resize_matrix(self, new_size: int) -> None:
        """Resize the adjacency matrix (expensive operation)."""
        old_size = self._matrix.shape[0]
        if new_size <= old_size:
            return

        new_matrix = np.zeros((new_size, new_size), dtype=np.float64)
        new_matrix[:old_size, :old_size] = self._matrix
        self._matrix = new_matrix

    def add_vertex(self, vertex: Vertex) -> None:
        """Add a vertex to the matrix."""
        if vertex.id in self._vertices:
            # Idempotent for new contract? Or raise?
            # Old code raised ValueError. New contract says idempotent.
            # We'll update vertex data but keep structure
            self._vertices[vertex.id] = vertex
            return

        next_index = len(self._vertices)
        if next_index >= self._matrix.shape[0]:
            new_size = self._matrix.shape[0] * 2
            self._resize_matrix(new_size)

        self._vertices[vertex.id] = vertex
        self._vertex_index[vertex.id] = next_index
        self._index_vertex.append(vertex.id)

    def add_edge(self, edge: Edge) -> None:
        """Add an edge to the matrix."""
        if edge.source not in self._vertices:
            msg = f"Source vertex {edge.source!r} not found"
            raise KeyError(msg)
        if edge.target not in self._vertices:
            msg = f"Target vertex {edge.target!r} not found"
            raise KeyError(msg)

        src_idx = self._vertex_index[edge.source]
        tgt_idx = self._vertex_index[edge.target]

        if self._matrix[src_idx, tgt_idx] != 0:
            msg = f"Edge {edge.source!r} -> {edge.target!r} already exists"
            raise ValueError(msg)

        self._matrix[src_idx, tgt_idx] = edge.weight
        if not self._directed:
            self._matrix[tgt_idx, src_idx] = edge.weight

        edge_key = (edge.source, edge.target)
        self._edges[edge_key] = edge
        if not self._directed:
            self._edges[(edge.target, edge.source)] = edge

    def remove_vertex(self, vertex_id: Any) -> None:
        """Remove a vertex from the matrix."""
        if vertex_id not in self._vertices:
            msg = f"Vertex {vertex_id!r} not found"
            raise KeyError(msg)

        idx_to_remove = self._vertex_index[vertex_id]

        del self._vertices[vertex_id]
        del self._vertex_index[vertex_id]
        del self._index_vertex[idx_to_remove]

        for i in range(idx_to_remove, len(self._index_vertex)):
            vid = self._index_vertex[i]
            self._vertex_index[vid] = i

        mask = np.ones(self._matrix.shape[0], dtype=bool)
        mask[idx_to_remove] = False
        self._matrix = self._matrix[mask][:, mask]

        edges_to_remove = [
            key for key in self._edges if key[0] == vertex_id or key[1] == vertex_id
        ]
        for key in edges_to_remove:
            del self._edges[key]

    def remove_edge(self, source: Any, target: Any) -> None:
        """Remove an edge from the matrix."""
        edge_key = (source, target)
        if edge_key not in self._edges:
            msg = f"Edge {source!r} -> {target!r} not found"
            raise KeyError(msg)

        src_idx = self._vertex_index[source]
        tgt_idx = self._vertex_index[target]

        self._matrix[src_idx, tgt_idx] = 0
        if not self._directed:
            self._matrix[tgt_idx, src_idx] = 0

        del self._edges[edge_key]
        if not self._directed:
            self._edges.pop((target, source), None)

    def has_edge(self, source: Any, target: Any) -> bool:
        """Check if edge exists."""
        if source not in self._vertices or target not in self._vertices:
            return False

        src_idx = self._vertex_index[source]
        tgt_idx = self._vertex_index[target]
        return self._matrix[src_idx, tgt_idx] != 0

    def get_edge(self, source: Any, target: Any) -> Edge:
        """Get edge object."""
        edge_key = (source, target)
        if edge_key not in self._edges:
            msg = f"Edge {source!r} -> {target!r} not found"
            raise ValueError(msg)
        return self._edges[edge_key]

    def get_all_edges(self, source: Any, target: Any) -> list[Edge]:
        """Retrieve all edges (returns list of 0 or 1 element)."""
        try:
            return [self.get_edge(source, target)]
        except ValueError:
            return []

    def get_neighbors(self, vertex_id: Any) -> Iterable[Any]:
        """Get neighbors of a vertex."""
        if vertex_id not in self._vertices:
            msg = f"Vertex {vertex_id!r} not found"
            raise KeyError(msg)

        idx = self._vertex_index[vertex_id]
        neighbor_indices = np.nonzero(self._matrix[idx])[0]
        return {self._index_vertex[i] for i in neighbor_indices}

    def vertex_count(self) -> int:
        """Get total number of vertices."""
        return len(self._vertices)

    def edge_count(self) -> int:
        """Get total number of edges."""
        if self._directed:
            return len(self._edges)
        return len(self._edges) // 2

    # --- Methods required by SimpleGraph ---

    def has_vertex(self, vertex_id: Any) -> bool:
        """Check if vertex exists."""
        return vertex_id in self._vertices

    def get_vertex(self, vertex_id: Any) -> Vertex:
        """Get vertex object."""
        if vertex_id not in self._vertices:
            msg = f"Vertex {vertex_id!r} not found"
            raise KeyError(msg)
        return self._vertices[vertex_id]

    def vertices(self) -> Iterator[Vertex]:
        """Iterate over all vertices."""
        yield from self._vertices.values()

    def edges(self) -> Iterator[Edge]:
        """Iterate over all edges."""
        seen = set()
        for edge in self._edges.values():
            if not self._directed:
                edge_id = frozenset([edge.source, edge.target])
                if edge_id in seen:
                    continue
                seen.add(edge_id)
            yield edge

    def clear(self) -> None:
        """Remove all vertices and edges."""
        self._matrix.fill(0)
        self._vertices.clear()
        self._vertex_index.clear()
        self._index_vertex.clear()
        self._edges.clear()

    def get_matrix(self) -> np.ndarray:
        """Get the adjacency matrix (copy)."""
        n = len(self._vertices)
        return self._matrix[:n, :n].copy()
