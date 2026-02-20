"""
Base abstract graph class defining the contract for all graph types.

This module implements the foundation of the graph library using SOLID principles:
- Single Responsibility: Each method has one clear purpose
- Open/Closed: Extensible through inheritance without modification
- Liskov Substitution: All graph types can be used interchangeably
- Interface Segregation: Separate interfaces for read/write operations
- Dependency Inversion: Depends on abstractions (representations)
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterator
from typing import TYPE_CHECKING, Any, Generic, TypeVar

if TYPE_CHECKING:
    from packages.core.edge import Edge
    from packages.core.vertex import Vertex
    from packages.representations.base_representation import GraphRepresentation

# Type variables for generic graph operations
V = TypeVar("V")  # Vertex type
E = TypeVar("E")  # Edge type


class BaseGraph(ABC, Generic[V, E]):
    """
    Abstract base class for all graph implementations.

    This class defines the contract that all graph types must implement,
    following the Template Method pattern for common operations.

    Attributes:
        _representation: Strategy pattern - the internal representation of the graph
        _directed: Whether the graph is directed
        _observers: List of observers for change notifications (Observer pattern)

    Type Parameters:
        V: Type of vertices (constrained to Vertex or its subclasses)
        E: Type of edges (constrained to Edge or its subclasses)

    Examples:
        >>> # Create a concrete graph implementation
        >>> graph = SimpleGraph(representation="adjacency_list")
        >>> graph.add_vertex("A", attributes={"color": "red"})
        >>> graph.add_edge("A", "B", weight=5.0)
    """

    __slots__ = ("_representation", "_directed", "_observers", "_metadata")

    def __init__(
        self,
        *,
        directed: bool = False,
        representation: str = "adjacency_list",
        **kwargs: Any,
    ) -> None:
        """
        Initialize base graph with specified representation strategy.

        Args:
            directed: Whether the graph is directed
            representation: Strategy for internal representation
                ("adjacency_list", "adjacency_matrix", "edge_list")
            **kwargs: Additional metadata for the graph

        Raises:
            ValueError: If representation type is not supported
        """
        self._directed = directed
        self._representation: GraphRepresentation = self._create_representation(representation)
        self._observers: list[Any] = []
        self._metadata: dict[str, Any] = kwargs

    @abstractmethod
    def _create_representation(self, repr_type: str) -> GraphRepresentation:
        """
        Factory method for creating representation strategy.

        This implements the Factory Method pattern, allowing subclasses
        to customize which representations are valid for their graph type.

        Args:
            repr_type: Type of representation to create

        Returns:
            GraphRepresentation instance

        Raises:
            ValueError: If representation type is not supported by this graph type
        """
        ...

    @abstractmethod
    def add_vertex(self, vertex_id: V, **attributes: Any) -> None:
        """
        Add a vertex to the graph.

        Args:
            vertex_id: Unique identifier for the vertex
            **attributes: Arbitrary key-value pairs for vertex metadata

        Raises:
            ValueError: If vertex already exists or violates graph constraints
        """
        ...

    @abstractmethod
    def add_edge(
        self,
        source: V,
        target: V,
        *,
        weight: float = 1.0,
        **attributes: Any,
    ) -> None:
        """
        Add an edge to the graph.

        Args:
            source: Source vertex identifier
            target: Target vertex identifier
            weight: Edge weight (default: 1.0)
            **attributes: Arbitrary key-value pairs for edge metadata

        Raises:
            ValueError: If edge violates graph constraints (e.g., self-loop in simple graph)
            KeyError: If source or target vertex doesn't exist
        """
        ...

    @abstractmethod
    def remove_vertex(self, vertex_id: V) -> None:
        """
        Remove a vertex and all its incident edges from the graph.

        Args:
            vertex_id: Identifier of vertex to remove

        Raises:
            KeyError: If vertex doesn't exist
        """
        ...

    @abstractmethod
    def remove_edge(self, source: V, target: V) -> None:
        """
        Remove an edge from the graph.

        Args:
            source: Source vertex identifier
            target: Target vertex identifier

        Raises:
            KeyError: If edge doesn't exist
        """
        ...

    @abstractmethod
    def has_vertex(self, vertex_id: V) -> bool:
        """
        Check if vertex exists in the graph.

        Time Complexity: O(1) for most representations

        Args:
            vertex_id: Identifier to check

        Returns:
            True if vertex exists, False otherwise
        """
        ...

    @abstractmethod
    def has_edge(self, source: V, target: V) -> bool:
        """
        Check if edge exists in the graph.

        Time Complexity: O(1) for adjacency list/matrix, O(E) for edge list

        Args:
            source: Source vertex identifier
            target: Target vertex identifier

        Returns:
            True if edge exists, False otherwise
        """
        ...

    @abstractmethod
    def get_neighbors(self, vertex_id: V) -> set[V]:
        """
        Get all neighbors of a vertex.

        For directed graphs, returns outgoing neighbors only.

        Args:
            vertex_id: Vertex to get neighbors for

        Returns:
            Set of neighboring vertex identifiers

        Raises:
            KeyError: If vertex doesn't exist
        """
        ...

    @abstractmethod
    def vertices(self) -> Iterator[Vertex]:
        """
        Iterate over all vertices in the graph.

        Yields:
            Vertex objects with their attributes
        """
        ...

    @abstractmethod
    def edges(self) -> Iterator[Edge]:
        """
        Iterate over all edges in the graph.

        Yields:
            Edge objects with their attributes
        """
        ...

    def degree(self, vertex_id: V) -> int:
        """
        Get degree of a vertex (number of incident edges).

        For directed graphs, returns out-degree.

        Args:
            vertex_id: Vertex to calculate degree for

        Returns:
            Degree of the vertex

        Raises:
            KeyError: If vertex doesn't exist
        """
        return len(self.get_neighbors(vertex_id))

    def is_directed(self) -> bool:
        """
        Check if graph is directed.

        Returns:
            True if graph is directed, False otherwise.

        Examples:
            >>> graph = SimpleGraph(directed=True)
            >>> graph.is_directed()
            True
        """
        return self._directed

    def get_edge_weight(self, source: V, target: V) -> float:
        """
        Get weight of edge between source and target.
        Returns weight of first edge found if multiple exist.
        """
        return self.get_edge(source, target).weight

    def vertex_count(self) -> int:
        """Get total number of vertices."""
        return len(list(self.vertices()))

    def edge_count(self) -> int:
        """Get total number of edges."""
        return len(list(self.edges()))

    def get_vertices(self) -> list[V]:
        """Get list of all vertex IDs."""
        return [v.id for v in self.vertices()]

    def get_edges(self) -> list[Edge]:
        """Get list of all edges."""
        return list(self.edges())

    def convert_representation(self, new_repr_type: str) -> None:
        """
        Convert to a different internal representation (Strategy pattern).

        This allows dynamic switching between representations based on
        performance characteristics or graph density.

        Args:
            new_repr_type: Target representation type

        Raises:
            ValueError: If conversion is not supported

        Examples:
            >>> graph = SimpleGraph(representation="adjacency_list")
            >>> graph.convert_representation("adjacency_matrix")
        """
        if new_repr_type == type(self._representation).__name__.lower():
            return  # Already using this representation

        # Create new representation and transfer data
        new_repr = self._create_representation(new_repr_type)
        for vertex in self.vertices():
            new_repr.add_vertex(vertex)
        for edge in self.edges():
            new_repr.add_edge(edge)

        self._representation = new_repr
        self._notify_observers("representation_changed", new_repr_type)

    def attach_observer(self, observer: Any) -> None:
        """Attach an observer for graph change notifications (Observer pattern)."""
        self._observers.append(observer)

    def detach_observer(self, observer: Any) -> None:
        """Detach an observer."""
        self._observers.remove(observer)

    def _notify_observers(self, event: str, *args: Any) -> None:
        """Notify all observers of a graph change."""
        for observer in self._observers:
            if hasattr(observer, "update"):
                observer.update(event, *args)

    def __repr__(self) -> str:
        """String representation for debugging."""
        return (
            f"{self.__class__.__name__}("
            f"vertices={self.vertex_count()}, "
            f"edges={self.edge_count()}, "
            f"directed={self._directed})"
        )

    def __len__(self) -> int:
        """Return number of vertices."""
        return self.vertex_count()
