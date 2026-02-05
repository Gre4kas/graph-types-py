"""
Adjacency matrix representation for dense graphs.

This module implements the adjacency matrix representation using NumPy arrays
for O(1) edge lookups and efficient matrix operations. Optimal for dense graphs
where |E| ≈ |V|².

Time Complexity:
- Add vertex: O(|V|²) - requires matrix resize
- Add edge: O(1)
- Remove vertex: O(|V|²) - requires matrix resize
- Remove edge: O(1)
- Has vertex: O(1)
- Has edge: O(1)
- Get neighbors: O(|V|)

Space Complexity: O(|V|²)
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import numpy as np

from packages.representations.base_representation import GraphRepresentation

if TYPE_CHECKING:
    from collections.abc import Iterator

    from packages.core.edge import Edge
    from packages.core.vertex import Vertex


class AdjacencyMatrixRepresentation(GraphRepresentation):
    """
    Adjacency matrix representation using NumPy 2D array.

    This representation is ideal for dense graphs and when matrix operations
    (shortest paths, connectivity) are frequently needed.

    Attributes:
        _matrix: NumPy 2D array where matrix[i][j] represents edge weight
        _vertices: Dictionary mapping vertex_id -> Vertex object
        _vertex_index: Dictionary mapping vertex_id -> matrix index
        _index_vertex: List mapping matrix index -> vertex_id
        _edges: Dictionary storing Edge objects
        _directed: Whether the graph is directed

    Examples:
        >>> repr = AdjacencyMatrixRepresentation(directed=False)
        >>> repr.add_vertex(Vertex(id="A"))
        >>> repr.add_vertex(Vertex(id="B"))
        >>> repr.add_edge(Edge(source="A", target="B", weight=5.0))
        >>> repr.has_edge("A", "B")
        True
    """

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
        """
        Initialize adjacency matrix representation.

        Args:
            directed: Whether the graph is directed
            initial_capacity: Initial matrix size (grows dynamically)
        """
        self._matrix = np.zeros((initial_capacity, initial_capacity), dtype=np.float64)
        self._vertices: dict[Any, Vertex] = {}
        self._vertex_index: dict[Any, int] = {}
        self._index_vertex: list[Any] = []
        self._edges: dict[tuple[Any, Any], Edge] = {}
        self._directed = directed

    def _resize_matrix(self, new_size: int) -> None:
        """
        Resize the adjacency matrix (expensive operation).

        Time Complexity: O(|V|²)

        Args:
            new_size: New matrix dimension
        """
        old_size = self._matrix.shape[0]
        if new_size <= old_size:
            return

        # Create larger matrix and copy old data
        new_matrix = np.zeros((new_size, new_size), dtype=np.float64)
        new_matrix[:old_size, :old_size] = self._matrix
        self._matrix = new_matrix

    def add_vertex(self, vertex: Vertex) -> None:
        """
        Add a vertex to the matrix.

        Time Complexity: O(|V|²) if resize needed, O(1) otherwise

        Args:
            vertex: Vertex object to add

        Raises:
            ValueError: If vertex already exists
        """
        if vertex.id in self._vertices:
            msg = f"Vertex {vertex.id!r} already exists"
            raise ValueError(msg)

        # Check if resize needed
        next_index = len(self._vertices)
        if next_index >= self._matrix.shape[0]:
            new_size = self._matrix.shape[0] * 2
            self._resize_matrix(new_size)

        # Add vertex
        self._vertices[vertex.id] = vertex
        self._vertex_index[vertex.id] = next_index
        self._index_vertex.append(vertex.id)

    def add_edge(self, edge: Edge) -> None:
        """
        Add an edge to the matrix.

        Time Complexity: O(1)

        Args:
            edge: Edge object to add

        Raises:
            KeyError: If source or target vertex doesn't exist
            ValueError: If edge already exists
        """
        if edge.source not in self._vertices:
            msg = f"Source vertex {edge.source!r} not found"
            raise KeyError(msg)
        if edge.target not in self._vertices:
            msg = f"Target vertex {edge.target!r} not found"
            raise KeyError(msg)

        # Get matrix indices
        src_idx = self._vertex_index[edge.source]
        tgt_idx = self._vertex_index[edge.target]

        # Check for existing edge (non-zero weight)
        if self._matrix[src_idx, tgt_idx] != 0:
            msg = f"Edge {edge.source!r} -> {edge.target!r} already exists"
            raise ValueError(msg)

        # Add edge weight to matrix
        self._matrix[src_idx, tgt_idx] = edge.weight
        if not self._directed:
            self._matrix[tgt_idx, src_idx] = edge.weight

        # Store edge object
        edge_key = (edge.source, edge.target)
        self._edges[edge_key] = edge
        if not self._directed:
            self._edges[(edge.target, edge.source)] = edge

    def remove_vertex(self, vertex_id: Any) -> None:
        """
        Remove a vertex from the matrix.

        Time Complexity: O(|V|²) - requires matrix reorganization

        Args:
            vertex_id: Identifier of vertex to remove

        Raises:
            KeyError: If vertex doesn't exist
        """
        if vertex_id not in self._vertices:
            msg = f"Vertex {vertex_id!r} not found"
            raise KeyError(msg)

        # Get index to remove
        idx_to_remove = self._vertex_index[vertex_id]

        # Remove from vertex mappings
        del self._vertices[vertex_id]
        del self._vertex_index[vertex_id]
        del self._index_vertex[idx_to_remove]

        # Update indices for remaining vertices
        for i in range(idx_to_remove, len(self._index_vertex)):
            vid = self._index_vertex[i]
            self._vertex_index[vid] = i

        # Remove row and column from matrix
        n = len(self._vertices)
        mask = np.ones(self._matrix.shape[0], dtype=bool)
        mask[idx_to_remove] = False
        self._matrix = self._matrix[mask][:, mask]

        # Remove all edges involving this vertex
        edges_to_remove = [
            key for key in self._edges if key[0] == vertex_id or key[1] == vertex_id
        ]
        for key in edges_to_remove:
            del self._edges[key]

    def remove_edge(self, source: Any, target: Any) -> None:
        """
        Remove an edge from the matrix.

        Time Complexity: O(1)

        Args:
            source: Source vertex identifier
            target: Target vertex identifier

        Raises:
            KeyError: If edge doesn't exist
        """
        edge_key = (source, target)
        if edge_key not in self._edges:
            msg = f"Edge {source!r} -> {target!r} not found"
            raise KeyError(msg)

        # Get matrix indices
        src_idx = self._vertex_index[source]
        tgt_idx = self._vertex_index[target]

        # Remove edge weight from matrix
        self._matrix[src_idx, tgt_idx] = 0
        if not self._directed:
            self._matrix[tgt_idx, src_idx] = 0

        # Remove edge object
        del self._edges[edge_key]
        if not self._directed:
            self._edges.pop((target, source), None)

    def has_vertex(self, vertex_id: Any) -> bool:
        """Check if vertex exists. Time Complexity: O(1)"""
        return vertex_id in self._vertices

    def has_edge(self, source: Any, target: Any) -> bool:
        """Check if edge exists. Time Complexity: O(1)"""
        if source not in self._vertices or target not in self._vertices:
            return False

        src_idx = self._vertex_index[source]
        tgt_idx = self._vertex_index[target]
        return self._matrix[src_idx, tgt_idx] != 0

    def get_neighbors(self, vertex_id: Any) -> set[Any]:
        """
        Get neighbors of a vertex.

        Time Complexity: O(|V|) - scans matrix row

        Args:
            vertex_id: Vertex to get neighbors for

        Returns:
            Set of neighbor vertex identifiers

        Raises:
            KeyError: If vertex doesn't exist
        """
        if vertex_id not in self._vertices:
            msg = f"Vertex {vertex_id!r} not found"
            raise KeyError(msg)

        idx = self._vertex_index[vertex_id]
        # Find all non-zero entries in this row
        neighbor_indices = np.nonzero(self._matrix[idx])[0]
        return {self._index_vertex[i] for i in neighbor_indices}

    def get_vertex(self, vertex_id: Any) -> Vertex:
        """Get vertex object by ID. Time Complexity: O(1)"""
        if vertex_id not in self._vertices:
            msg = f"Vertex {vertex_id!r} not found"
            raise KeyError(msg)
        return self._vertices[vertex_id]

    def get_edge(self, source: Any, target: Any) -> Edge:
        """Get edge object. Time Complexity: O(1)"""
        edge_key = (source, target)
        if edge_key not in self._edges:
            msg = f"Edge {source!r} -> {target!r} not found"
            raise KeyError(msg)
        return self._edges[edge_key]

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

    def vertex_count(self) -> int:
        """Get total number of vertices."""
        return len(self._vertices)

    def edge_count(self) -> int:
        """Get total number of edges."""
        if self._directed:
            return len(self._edges)
        return len(self._edges) // 2

    def clear(self) -> None:
        """Remove all vertices and edges."""
        self._matrix.fill(0)
        self._vertices.clear()
        self._vertex_index.clear()
        self._index_vertex.clear()
        self._edges.clear()

    def get_matrix(self) -> np.ndarray:
        """
        Get the adjacency matrix (copy).

        Returns:
            NumPy 2D array representing the graph
        """
        n = len(self._vertices)
        return self._matrix[:n, :n].copy()

    def __repr__(self) -> str:
        """String representation for debugging."""
        return (
            f"AdjacencyMatrixRepresentation("
            f"vertices={self.vertex_count()}, "
            f"edges={self.edge_count()}, "
            f"directed={self._directed})"
        )
