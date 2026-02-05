"""
Base representation class implementing Strategy pattern.

This module defines the abstract interface for different graph representations,
allowing dynamic switching between adjacency list, matrix, and edge list formats.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Iterator

    from packages.core.edge import Edge
    from packages.core.vertex import Vertex


class GraphRepresentation(ABC):
    """
    Abstract base class for graph representation strategies.

    This implements the Strategy pattern, allowing different internal
    representations (adjacency list, matrix, edge list) to be swapped
    at runtime based on performance characteristics.

    Subclasses must implement all abstract methods to provide a complete
    representation strategy.

    Examples:
        >>> repr = AdjacencyListRepresentation()
        >>> repr.add_vertex(Vertex(id="A"))
        >>> repr.add_edge(Edge(source="A", target="B"))
    """

    __slots__ = ()

    @abstractmethod
    def add_vertex(self, vertex: Vertex) -> None:
        """
        Add a vertex to the representation.

        Args:
            vertex: Vertex object to add

        Raises:
            ValueError: If vertex already exists
        """
        ...

    @abstractmethod
    def add_edge(self, edge: Edge) -> None:
        """
        Add an edge to the representation.

        Args:
            edge: Edge object to add

        Raises:
            KeyError: If source or target vertex doesn't exist
            ValueError: If edge already exists (for non-multi graphs)
        """
        ...

    @abstractmethod
    def remove_vertex(self, vertex_id: Any) -> None:
        """
        Remove a vertex and all incident edges.

        Args:
            vertex_id: Identifier of vertex to remove

        Raises:
            KeyError: If vertex doesn't exist
        """
        ...

    @abstractmethod
    def remove_edge(self, source: Any, target: Any) -> None:
        """
        Remove an edge from the representation.

        Args:
            source: Source vertex identifier
            target: Target vertex identifier

        Raises:
            KeyError: If edge doesn't exist
        """
        ...

    @abstractmethod
    def has_vertex(self, vertex_id: Any) -> bool:
        """
        Check if vertex exists.

        Args:
            vertex_id: Identifier to check

        Returns:
            True if vertex exists
        """
        ...

    @abstractmethod
    def has_edge(self, source: Any, target: Any) -> bool:
        """
        Check if edge exists.

        Args:
            source: Source vertex identifier
            target: Target vertex identifier

        Returns:
            True if edge exists
        """
        ...

    @abstractmethod
    def get_neighbors(self, vertex_id: Any) -> set[Any]:
        """
        Get neighbors of a vertex.

        Args:
            vertex_id: Vertex to get neighbors for

        Returns:
            Set of neighbor vertex identifiers

        Raises:
            KeyError: If vertex doesn't exist
        """
        ...

    @abstractmethod
    def get_vertex(self, vertex_id: Any) -> Vertex:
        """
        Get vertex object by ID.

        Args:
            vertex_id: Vertex identifier

        Returns:
            Vertex object

        Raises:
            KeyError: If vertex doesn't exist
        """
        ...

    @abstractmethod
    def get_edge(self, source: Any, target: Any) -> Edge:
        """
        Get edge object.

        Args:
            source: Source vertex identifier
            target: Target vertex identifier

        Returns:
            Edge object

        Raises:
            KeyError: If edge doesn't exist
        """
        ...

    @abstractmethod
    def vertices(self) -> Iterator[Vertex]:
        """Iterate over all vertices."""
        ...

    @abstractmethod
    def edges(self) -> Iterator[Edge]:
        """Iterate over all edges."""
        ...

    @abstractmethod
    def vertex_count(self) -> int:
        """Get total number of vertices."""
        ...

    @abstractmethod
    def edge_count(self) -> int:
        """Get total number of edges."""
        ...

    @abstractmethod
    def clear(self) -> None:
        """Remove all vertices and edges."""
        ...
