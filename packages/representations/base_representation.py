"""Abstract base class for graph representation strategies.

This module defines the unified contract for all graph storage implementations,
following the Strategy pattern for clean polymorphism.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Iterable

if TYPE_CHECKING:
    from collections.abc import Iterator

    from packages.core.edge import Edge
    from packages.core.vertex import Vertex, VertexId


class GraphRepresentation(ABC):
    """Abstract base class for graph storage strategies."""

    __slots__ = ()

    @abstractmethod
    def add_vertex(self, vertex: Vertex[VertexId]) -> None:
        """Add a vertex to the graph representation."""
        ...

    @abstractmethod
    def remove_vertex(self, vertex_id: VertexId) -> None:
        """Remove a vertex and all incident edges."""
        ...

    @abstractmethod
    def add_edge(self, edge: Edge[VertexId]) -> None:
        """Add an edge to the graph representation."""
        ...

    @abstractmethod
    def remove_edge(self, source: VertexId, target: VertexId) -> None:
        """Remove an edge from the graph representation."""
        ...

    @abstractmethod
    def has_edge(self, source: VertexId, target: VertexId) -> bool:
        """Check if an edge exists between two vertices."""
        ...

    @abstractmethod
    def get_edge(self, source: VertexId, target: VertexId) -> Edge[VertexId]:
        """Retrieve a single edge between two vertices."""
        ...

    @abstractmethod
    def get_all_edges(
        self,
        source: VertexId,
        target: VertexId,
    ) -> list[Edge[VertexId]]:
        """Retrieve all edges between two vertices."""
        ...

    @abstractmethod
    def get_neighbors(self, vertex_id: VertexId) -> Iterable[VertexId]:
        """Retrieve all neighbors of a vertex."""
        ...

    @abstractmethod
    def vertex_count(self) -> int:
        """Get the total number of vertices in the graph."""
        ...

    @abstractmethod
    def edge_count(self) -> int:
        """Get the total number of edges in the graph."""
        ...

    # --- Methods required by SimpleGraph and other consumers ---

    @abstractmethod
    def has_vertex(self, vertex_id: VertexId) -> bool:
        """Check if a vertex exists in the graph."""
        ...

    @abstractmethod
    def get_vertex(self, vertex_id: VertexId) -> Vertex[VertexId]:
        """Retrieve a vertex object by its ID."""
        ...

    @abstractmethod
    def vertices(self) -> Iterator[Vertex[VertexId]]:
        """Iterate over all vertices in the graph."""
        ...

    @abstractmethod
    def edges(self) -> Iterator[Edge[VertexId]]:
        """Iterate over all edges in the graph."""
        ...
