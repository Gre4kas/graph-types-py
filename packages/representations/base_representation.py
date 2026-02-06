"""Abstract base class for graph representation strategies.

This module defines the unified contract for all graph storage implementations,
following the Strategy pattern for clean polymorphism.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Iterable

if TYPE_CHECKING:
    from packages.core.edge import Edge
    from packages.core.vertex import Vertex, VertexId


class GraphRepresentation(ABC):
    """Abstract base class for graph storage strategies.

    This class defines the unified interface for all graph representation
    implementations (adjacency list, matrix, hypergraph, etc.). Each concrete
    strategy must implement all abstract methods to ensure consistent behavior.

    The design follows SOLID principles:
    - Single Responsibility: Each subclass handles one storage strategy
    - Open/Closed: Extensible without modifying base contract
    - Liskov Substitution: All implementations are interchangeable
    - Interface Segregation: Minimal, focused interface
    - Dependency Inversion: Depend on abstraction, not concretions

    Performance Requirements:
        - get_neighbors: O(1) amortized
        - has_edge: O(1) amortized
        - add_vertex: O(1) amortized
        - add_edge: O(1) amortized (simple graphs) or O(n) for multi-graphs

    Type Parameters:
        VertexId: Type of vertex identifier (str, int, or hashable)

    Notes:
        - Implementations must use __slots__ for memory efficiency
        - Input validation is handled by Pydantic models (Vertex, Edge)
        - Thread safety is NOT guaranteed by default

    Examples:
        >>> # Abstract class cannot be instantiated directly
        >>> repr = SimpleAdjacencyListRepresentation()
        >>> repr.add_vertex(Vertex(id="A"))
        >>> repr.add_edge(Edge(source="A", target="B"))
        >>> repr.has_edge("A", "B")
        True
    """

    __slots__ = ()

    @abstractmethod
    def add_vertex(self, vertex: Vertex[VertexId]) -> None:
        """Add a vertex to the graph representation.

        If the vertex already exists, this operation should be idempotent
        (no error, no duplicate).

        Args:
            vertex: Validated Vertex instance to add

        Time Complexity:
            O(1) amortized

        Examples:
            >>> repr.add_vertex(Vertex(id="A", attributes={"color": "red"}))
            >>> repr.add_vertex(Vertex(id="A"))  # Idempotent, no error
        """
        ...

    @abstractmethod
    def remove_vertex(self, vertex_id: VertexId) -> None:
        """Remove a vertex and all incident edges from the graph.

        Args:
            vertex_id: Identifier of the vertex to remove

        Raises:
            KeyError: If vertex does not exist in the graph

        Time Complexity:
            O(V + E) worst case (must remove all incident edges)

        Examples:
            >>> repr.remove_vertex("A")
            >>> repr.remove_vertex("NonExistent")  # Raises KeyError
        """
        ...

    @abstractmethod
    def add_edge(self, edge: Edge[VertexId]) -> None:
        """Add an edge to the graph representation.

        Behavior depends on the concrete implementation:
        - SimpleAdjacencyList: Raises error if edge already exists
        - MultiAdjacencyList: Allows duplicate edges (parallel edges)

        Args:
            edge: Validated Edge instance to add

        Raises:
            ValueError: If source or target vertex does not exist
            ValueError: If edge already exists (simple graphs only)

        Time Complexity:
            O(1) amortized for simple graphs
            O(n) for multigraphs (must check duplicates)

        Examples:
            >>> repr.add_edge(Edge(source="A", target="B", weight=5.0))
        """
        ...

    @abstractmethod
    def remove_edge(self, source: VertexId, target: VertexId) -> None:
        """Remove an edge from the graph representation.

        For multigraphs, this removes ALL edges between source and target.

        Args:
            source: Source vertex identifier
            target: Target vertex identifier

        Raises:
            ValueError: If edge does not exist

        Time Complexity:
            O(1) for simple graphs
            O(n) for multigraphs (must remove all parallel edges)

        Examples:
            >>> repr.remove_edge("A", "B")
            >>> repr.remove_edge("A", "NonExistent")  # Raises ValueError
        """
        ...

    @abstractmethod
    def has_edge(self, source: VertexId, target: VertexId) -> bool:
        """Check if an edge exists between two vertices.

        Args:
            source: Source vertex identifier
            target: Target vertex identifier

        Returns:
            True if at least one edge exists, False otherwise

        Time Complexity:
            O(1) amortized (critical hot path)

        Examples:
            >>> repr.has_edge("A", "B")
            True
            >>> repr.has_edge("A", "NonExistent")
            False
        """
        ...

    @abstractmethod
    def get_edge(self, source: VertexId, target: VertexId) -> Edge[VertexId]:
        """Retrieve a single edge between two vertices.

        For simple graphs, returns THE edge.
        For multigraphs, returns an arbitrary edge (use get_all_edges for all).

        Args:
            source: Source vertex identifier
            target: Target vertex identifier

        Returns:
            Edge object connecting source and target

        Raises:
            ValueError: If no edge exists between the vertices

        Time Complexity:
            O(1) amortized

        Examples:
            >>> edge = repr.get_edge("A", "B")
            >>> edge.weight
            5.0
        """
        ...

    @abstractmethod
    def get_all_edges(
        self,
        source: VertexId,
        target: VertexId,
    ) -> list[Edge[VertexId]]:
        """Retrieve all edges between two vertices.

        For simple graphs, returns a list of 0 or 1 element.
        For multigraphs, returns all parallel edges.

        Args:
            source: Source vertex identifier
            target: Target vertex identifier

        Returns:
            List of Edge objects (empty if no edge exists)

        Time Complexity:
            O(1) for simple graphs
            O(k) for multigraphs where k is number of parallel edges

        Examples:
            >>> edges = repr.get_all_edges("A", "B")
            >>> len(edges)
            3  # Three parallel edges in a multigraph
        """
        ...

    @abstractmethod
    def get_neighbors(self, vertex_id: VertexId) -> Iterable[VertexId]:
        """Retrieve all neighbors of a vertex.

        For multigraphs with multiple edges to the same neighbor,
        the neighbor appears only once in the result.

        Args:
            vertex_id: Identifier of the vertex

        Returns:
            Iterable of unique neighbor vertex identifiers

        Raises:
            KeyError: If vertex does not exist in the graph

        Time Complexity:
            O(1) to get the neighbor collection (critical hot path)
            O(k) to iterate all k neighbors

        Examples:
            >>> list(repr.get_neighbors("A"))
            ['B', 'C', 'D']
        """
        ...

    @abstractmethod
    def vertex_count(self) -> int:
        """Get the total number of vertices in the graph.

        Returns:
            Number of vertices

        Time Complexity:
            O(1)

        Examples:
            >>> repr.vertex_count()
            5
        """
        ...

    @abstractmethod
    def edge_count(self) -> int:
        """Get the total number of edges in the graph.

        For multigraphs, counts all parallel edges separately.

        Returns:
            Number of edges

        Time Complexity:
            O(1) amortized

        Examples:
            >>> repr.edge_count()
            10
        """
        ...
