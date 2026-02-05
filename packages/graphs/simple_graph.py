"""
Simple graph implementation (no loops, no multiple edges).

This module implements a simple graph from graph theory:
- No self-loops (edges from vertex to itself)
- No multiple edges between same vertex pair
- Can be directed or undirected

Mathematical definition: G = (V, E) where E ⊆ V × V and no (v, v) ∈ E
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from packages.core.base_graph import BaseGraph
from packages.core.edge import Edge
from packages.core.vertex import Vertex
from packages.representations.adjacency_list import AdjacencyListRepresentation
from packages.representations.adjacency_matrix import AdjacencyMatrixRepresentation
from packages.representations.base_representation import GraphRepresentation
from packages.utils.exceptions import GraphConstraintError, VertexNotFoundError

if TYPE_CHECKING:
    from collections.abc import Iterator


class SimpleGraph(BaseGraph[Any, Any]):
    """
    Simple graph with no loops and no multiple edges.

    This is the most basic graph type in graph theory, suitable for
    representing relationships where:
    - No entity relates to itself (no self-loops)
    - Each pair of entities has at most one connection

    Examples:
        >>> # Create undirected simple graph
        >>> graph = SimpleGraph(representation="adjacency_list")
        >>> graph.add_vertex("A", color="red")
        >>> graph.add_vertex("B", color="blue")
        >>> graph.add_edge("A", "B", weight=5.0)
        >>> graph.has_edge("A", "B")
        True
        >>> graph.degree("A")
        1

        >>> # Attempt to add self-loop (raises error)
        >>> graph.add_edge("A", "A", weight=1.0)  # Raises GraphConstraintError

        >>> # Convert representation
        >>> graph.convert_representation("adjacency_matrix")

    Attributes:
        Inherited from BaseGraph:
        - _representation: Internal graph representation strategy
        - _directed: Whether graph is directed
        - _observers: List of change observers
        - _metadata: Additional graph metadata
    """

    def __init__(
        self,
        *,
        directed: bool = False,
        representation: str = "adjacency_list",
        **kwargs: Any,
    ) -> None:
        """
        Initialize a simple graph.

        Args:
            directed: Whether the graph is directed (default: False)
            representation: Internal representation strategy:
                - "adjacency_list" (default): O(|V| + |E|) space, sparse graphs
                - "adjacency_matrix": O(|V|²) space, dense graphs
                - "edge_list": O(|E|) space, minimal storage
            **kwargs: Additional graph metadata

        Examples:
            >>> graph = SimpleGraph()  # Undirected, adjacency list
            >>> graph_directed = SimpleGraph(directed=True)
            >>> graph_matrix = SimpleGraph(representation="adjacency_matrix")
        """
        super().__init__(directed=directed, representation=representation, **kwargs)

    def _create_representation(self, repr_type: str) -> GraphRepresentation:
        """
        Factory method for creating representation strategy.

        Args:
            repr_type: Type of representation ("adjacency_list", "adjacency_matrix")

        Returns:
            GraphRepresentation instance

        Raises:
            ValueError: If representation type is not supported
        """
        repr_map = {
            "adjacency_list": AdjacencyListRepresentation,
            "adjacency_matrix": AdjacencyMatrixRepresentation,
        }

        if repr_type not in repr_map:
            supported = ", ".join(repr_map.keys())
            msg = f"Unsupported representation: {repr_type!r}. Supported: {supported}"
            raise ValueError(msg)

        return repr_map[repr_type](directed=self._directed)

    def add_vertex(self, vertex_id: Any, **attributes: Any) -> None:
        """
        Add a vertex to the graph.

        Time Complexity:
        - Adjacency list: O(1)
        - Adjacency matrix: O(|V|²) if resize needed

        Args:
            vertex_id: Unique identifier for the vertex
            **attributes: Arbitrary key-value pairs for vertex metadata

        Raises:
            ValueError: If vertex already exists

        Examples:
            >>> graph = SimpleGraph()
            >>> graph.add_vertex("A", color="red", weight=42)
            >>> graph.add_vertex("B", color="blue")
            >>> graph.add_vertex("A")  # Raises ValueError
        """
        vertex = Vertex(id=vertex_id, attributes=attributes)
        self._representation.add_vertex(vertex)
        self._notify_observers("vertex_added", vertex_id)

    def add_edge(
        self,
        source: Any,
        target: Any,
        *,
        weight: float = 1.0,
        **attributes: Any,
    ) -> None:
        """
        Add an edge to the graph.

        Simple graph constraints:
        - No self-loops: source != target
        - No multiple edges: edge must not already exist

        Time Complexity:
        - Adjacency list: O(1) average
        - Adjacency matrix: O(1)

        Args:
            source: Source vertex identifier
            target: Target vertex identifier
            weight: Edge weight (default: 1.0)
            **attributes: Arbitrary key-value pairs for edge metadata

        Raises:
            GraphConstraintError: If attempting to add self-loop
            ValueError: If edge already exists
            VertexNotFoundError: If source or target vertex doesn't exist

        Examples:
            >>> graph = SimpleGraph()
            >>> graph.add_vertex("A")
            >>> graph.add_vertex("B")
            >>> graph.add_edge("A", "B", weight=5.0, label="connection")
            >>> graph.add_edge("A", "A")  # Raises GraphConstraintError (self-loop)
            >>> graph.add_edge("A", "B")  # Raises ValueError (duplicate)
        """
        # Constraint: No self-loops in simple graphs
        if source == target:
            msg = f"Simple graphs cannot contain self-loops: {source!r} -> {source!r}"
            raise GraphConstraintError(msg)

        # Check vertices exist
        if not self._representation.has_vertex(source):
            msg = f"Source vertex {source!r} not found"
            raise VertexNotFoundError(msg)
        if not self._representation.has_vertex(target):
            msg = f"Target vertex {target!r} not found"
            raise VertexNotFoundError(msg)

        # Create and add edge
        edge = Edge(
            source=source,
            target=target,
            weight=weight,
            directed=self._directed,
            attributes=attributes,
        )
        self._representation.add_edge(edge)
        self._notify_observers("edge_added", source, target)

    def remove_vertex(self, vertex_id: Any) -> None:
        """
        Remove a vertex and all its incident edges.

        Time Complexity:
        - Adjacency list: O(degree(vertex))
        - Adjacency matrix: O(|V|²)

        Args:
            vertex_id: Identifier of vertex to remove

        Raises:
            VertexNotFoundError: If vertex doesn't exist

        Examples:
            >>> graph = SimpleGraph()
            >>> graph.add_vertex("A")
            >>> graph.add_edge("A", "B")
            >>> graph.remove_vertex("A")  # Also removes edge A-B
            >>> graph.has_vertex("A")
            False
        """
        if not self._representation.has_vertex(vertex_id):
            msg = f"Vertex {vertex_id!r} not found"
            raise VertexNotFoundError(msg)

        self._representation.remove_vertex(vertex_id)
        self._notify_observers("vertex_removed", vertex_id)

    def remove_edge(self, source: Any, target: Any) -> None:
        """
        Remove an edge from the graph.

        Time Complexity:
        - Adjacency list: O(1) average
        - Adjacency matrix: O(1)

        Args:
            source: Source vertex identifier
            target: Target vertex identifier

        Raises:
            KeyError: If edge doesn't exist

        Examples:
            >>> graph = SimpleGraph()
            >>> graph.add_edge("A", "B")
            >>> graph.remove_edge("A", "B")
            >>> graph.has_edge("A", "B")
            False
        """
        self._representation.remove_edge(source, target)
        self._notify_observers("edge_removed", source, target)

    def has_vertex(self, vertex_id: Any) -> bool:
        """
        Check if vertex exists in the graph.

        Time Complexity: O(1)

        Args:
            vertex_id: Identifier to check

        Returns:
            True if vertex exists, False otherwise

        Examples:
            >>> graph = SimpleGraph()
            >>> graph.add_vertex("A")
            >>> graph.has_vertex("A")
            True
            >>> graph.has_vertex("Z")
            False
        """
        return self._representation.has_vertex(vertex_id)

    def has_edge(self, source: Any, target: Any) -> bool:
        """
        Check if edge exists in the graph.

        Time Complexity:
        - Adjacency list/matrix: O(1)
        - Edge list: O(|E|)

        Args:
            source: Source vertex identifier
            target: Target vertex identifier

        Returns:
            True if edge exists, False otherwise

        Examples:
            >>> graph = SimpleGraph()
            >>> graph.add_edge("A", "B")
            >>> graph.has_edge("A", "B")
            True
            >>> graph.has_edge("B", "A")  # True for undirected
            True
        """
        return self._representation.has_edge(source, target)

    def get_neighbors(self, vertex_id: Any) -> set[Any]:
        """
        Get all neighbors of a vertex.

        For directed graphs, returns outgoing neighbors only.
        For undirected graphs, returns all adjacent vertices.

        Time Complexity:
        - Adjacency list: O(1)
        - Adjacency matrix: O(|V|)

        Args:
            vertex_id: Vertex to get neighbors for

        Returns:
            Set of neighboring vertex identifiers

        Raises:
            VertexNotFoundError: If vertex doesn't exist

        Examples:
            >>> graph = SimpleGraph()
            >>> graph.add_edge("A", "B")
            >>> graph.add_edge("A", "C")
            >>> sorted(graph.get_neighbors("A"))
            ['B', 'C']
        """
        if not self._representation.has_vertex(vertex_id):
            msg = f"Vertex {vertex_id!r} not found"
            raise VertexNotFoundError(msg)

        return self._representation.get_neighbors(vertex_id)

    def vertices(self) -> Iterator[Vertex]:
        """
        Iterate over all vertices in the graph.

        Yields:
            Vertex objects with their attributes

        Examples:
            >>> graph = SimpleGraph()
            >>> graph.add_vertex("A", color="red")
            >>> graph.add_vertex("B", color="blue")
            >>> for v in graph.vertices():
            ...     print(v.id, v.attributes)
            A {'color': 'red'}
            B {'color': 'blue'}
        """
        yield from self._representation.vertices()

    def edges(self) -> Iterator[Edge]:
        """
        Iterate over all edges in the graph.

        Yields:
            Edge objects with their attributes

        Examples:
            >>> graph = SimpleGraph()
            >>> graph.add_edge("A", "B", weight=5.0)
            >>> for e in graph.edges():
            ...     print(f"{e.source} -> {e.target}, weight={e.weight}")
            A -> B, weight=5.0
        """
        yield from self._representation.edges()

    def to_multigraph(self) -> Multigraph:
        """
        Convert to multigraph (allows multiple edges).

        Returns:
            New Multigraph instance with same vertices and edges

        Examples:
            >>> simple = SimpleGraph()
            >>> simple.add_edge("A", "B")
            >>> multi = simple.to_multigraph()
            >>> multi.add_edge("A", "B")  # Now allowed (second edge)
        """
        from packages.graphs.multigraph import Multigraph

        multi = Multigraph(directed=self._directed)
        for vertex in self.vertices():
            multi.add_vertex(vertex.id, **vertex.attributes)
        for edge in self.edges():
            multi.add_edge(edge.source, edge.target, weight=edge.weight, **edge.attributes)
        return multi

    def to_pseudograph(self) -> Pseudograph:
        """
        Convert to pseudograph (allows self-loops and multiple edges).

        Returns:
            New Pseudograph instance with same vertices and edges

        Examples:
            >>> simple = SimpleGraph()
            >>> simple.add_edge("A", "B")
            >>> pseudo = simple.to_pseudograph()
            >>> pseudo.add_edge("A", "A")  # Now allowed (self-loop)
        """
        from packages.graphs.pseudograph import Pseudograph

        pseudo = Pseudograph(directed=self._directed)
        for vertex in self.vertices():
            pseudo.add_vertex(vertex.id, **vertex.attributes)
        for edge in self.edges():
            pseudo.add_edge(edge.source, edge.target, weight=edge.weight, **edge.attributes)
        return pseudo
