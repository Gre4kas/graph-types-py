"""
Adjacency list representation for sparse graphs.

This module implements the adjacency list representation using dictionaries
and sets for O(1) average-case operations. Optimal for sparse graphs where
|E| << |V|².

Time Complexity:
- Add vertex: O(1)
- Add edge: O(1) average
- Remove vertex: O(degree(v))
- Remove edge: O(1) average
- Has vertex: O(1)
- Has edge: O(1) average
- Get neighbors: O(1)

Space Complexity: O(|V| + |E|)
"""

from __future__ import annotations

from collections import defaultdict
from typing import TYPE_CHECKING, Any

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

    Examples:
        >>> repr = AdjacencyListRepresentation(directed=False)
        >>> repr.add_vertex(Vertex(id="A"))
        >>> repr.add_vertex(Vertex(id="B"))
        >>> repr.add_edge(Edge(source="A", target="B", weight=5.0))
        >>> list(repr.get_neighbors("A"))
        ['B']
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
        """
        Add a vertex to the adjacency list.

        Time Complexity: O(1)

        Args:
            vertex: Vertex object to add

        Raises:
            ValueError: If vertex already exists
        """
        if vertex.id in self._vertices:
            msg = f"Vertex {vertex.id!r} already exists"
            raise ValueError(msg)

        self._vertices[vertex.id] = vertex
        self._adj_list[vertex.id]  # Initialize empty set via defaultdict

    def add_edge(self, edge: Edge) -> None:
        """
        Add an edge to the adjacency list.

        Time Complexity: O(1) average

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

        # Check for existing edge
        edge_key = (edge.source, edge.target)
        if edge_key in self._edges:
            msg = f"Edge {edge.source!r} -> {edge.target!r} already exists"
            raise ValueError(msg)

        # Add to adjacency list
        self._adj_list[edge.source].add(edge.target)
        if not self._directed:
            self._adj_list[edge.target].add(edge.source)

        # Store edge object
        self._edges[edge_key] = edge
        if not self._directed:
            # For undirected, store both directions
            self._edges[(edge.target, edge.source)] = edge

    def remove_vertex(self, vertex_id: Any) -> None:
        """
        Remove a vertex and all incident edges.

        Time Complexity: O(degree(vertex_id))

        Args:
            vertex_id: Identifier of vertex to remove

        Raises:
            KeyError: If vertex doesn't exist
        """
        if vertex_id not in self._vertices:
            msg = f"Vertex {vertex_id!r} not found"
            raise KeyError(msg)

        # Remove all edges involving this vertex
        neighbors = list(self._adj_list[vertex_id])
        for neighbor in neighbors:
            # Remove edge from adjacency list
            self._adj_list[neighbor].discard(vertex_id)
            # Remove edge object
            self._edges.pop((vertex_id, neighbor), None)
            self._edges.pop((neighbor, vertex_id), None)

        # Remove vertex
        del self._vertices[vertex_id]
        del self._adj_list[vertex_id]

        # Clean up edges where this vertex was source
        edges_to_remove = [
            key for key in self._edges if key[0] == vertex_id or key[1] == vertex_id
        ]
        for key in edges_to_remove:
            del self._edges[key]

    def remove_edge(self, source: Any, target: Any) -> None:
        """
        Remove an edge from the adjacency list.

        Time Complexity: O(1) average

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

        # Remove from adjacency list
        self._adj_list[source].discard(target)
        if not self._directed:
            self._adj_list[target].discard(source)

        # Remove edge object
        del self._edges[edge_key]
        if not self._directed:
            self._edges.pop((target, source), None)

    def has_vertex(self, vertex_id: Any) -> bool:
        """
        Check if vertex exists.

        Time Complexity: O(1)

        Args:
            vertex_id: Identifier to check

        Returns:
            True if vertex exists
        """
        return vertex_id in self._vertices

    def has_edge(self, source: Any, target: Any) -> bool:
        """
        Check if edge exists.

        Time Complexity: O(1) average

        Args:
            source: Source vertex identifier
            target: Target vertex identifier

        Returns:
            True if edge exists
        """
        return (source, target) in self._edges

    def get_neighbors(self, vertex_id: Any) -> set[Any]:
        """
        Get neighbors of a vertex.

        Time Complexity: O(1)

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
        return self._adj_list[vertex_id].copy()

    def get_vertex(self, vertex_id: Any) -> Vertex:
        """
        Get vertex object by ID.

        Time Complexity: O(1)

        Args:
            vertex_id: Vertex identifier

        Returns:
            Vertex object

        Raises:
            KeyError: If vertex doesn't exist
        """
        if vertex_id not in self._vertices:
            msg = f"Vertex {vertex_id!r} not found"
            raise KeyError(msg)
        return self._vertices[vertex_id]

    def get_edge(self, source: Any, target: Any) -> Edge:
        """
        Get edge object.

        Time Complexity: O(1) average

        Args:
            source: Source vertex identifier
            target: Target vertex identifier

        Returns:
            Edge object

        Raises:
            KeyError: If edge doesn't exist
        """
        edge_key = (source, target)
        if edge_key not in self._edges:
            msg = f"Edge {source!r} -> {target!r} not found"
            raise KeyError(msg)
        return self._edges[edge_key]

    def vertices(self) -> Iterator[Vertex]:
        """
        Iterate over all vertices.

        Yields:
            Vertex objects
        """
        yield from self._vertices.values()

    def edges(self) -> Iterator[Edge]:
        """
        Iterate over all edges.

        For undirected graphs, each edge is yielded once.

        Yields:
            Edge objects
        """
        seen = set()
        for edge in self._edges.values():
            # For undirected, avoid duplicates
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
        return len(self._edges) // 2  # Each undirected edge stored twice

    def clear(self) -> None:
        """Remove all vertices and edges."""
        self._adj_list.clear()
        self._vertices.clear()
        self._edges.clear()

    def __repr__(self) -> str:
        """String representation for debugging."""
        return (
            f"AdjacencyListRepresentation("
            f"vertices={self.vertex_count()}, "
            f"edges={self.edge_count()}, "
            f"directed={self._directed})"
        )
