"""
Edge list representation for minimal storage.

Optimal for: sparse graphs, serialization, disk storage, export/import.

Time Complexity:
- Add vertex: O(1)
- Add edge: O(1)
- Remove vertex: O(E)
- Remove edge: O(E)
- Has vertex: O(1)
- Has edge: O(E) - SLOW!
- Get neighbors: O(E) - SLOW!

Space Complexity: O(V + E) - most memory efficient
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from packages.representations.base_representation import GraphRepresentation

if TYPE_CHECKING:
    from collections.abc import Iterator

    from packages.core.edge import Edge
    from packages.core.vertex import Vertex


class EdgeListRepresentation(GraphRepresentation):
    """
    Edge list representation storing edges as a simple list.

    This is the most space-efficient representation but has slow
    neighbor queries. Best for:
    - Serialization and export
    - Sparse graphs with few queries
    - Minimal memory footprint
    - Batch processing

    Attributes:
        _vertices: Dictionary mapping vertex_id -> Vertex object
        _edges: List of all Edge objects
        _directed: Whether the graph is directed

    Examples:
        >>> from packages.core.vertex import Vertex
        >>> from packages.core.edge import Edge
        >>> 
        >>> repr = EdgeListRepresentation(directed=False)
        >>> repr.add_vertex(Vertex(id="A"))
        >>> repr.add_vertex(Vertex(id="B"))
        >>> repr.add_edge(Edge(source="A", target="B", weight=5.0))
        >>> repr.has_edge("A", "B")
        True
        >>> list(repr.get_neighbors("A"))
        ['B']
    """

    __slots__ = ("_vertices", "_edges", "_directed")

    def __init__(self, *, directed: bool = False) -> None:
        """
        Initialize edge list representation.

        Args:
            directed: Whether the graph is directed
        """
        self._vertices: dict[Any, Vertex] = {}
        self._edges: list[Edge] = []
        self._directed = directed

    def add_vertex(self, vertex: Vertex) -> None:
        """
        Add vertex to the representation.

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

    def add_edge(self, edge: Edge) -> None:
        """
        Add edge to the representation.

        Time Complexity: O(E) due to duplicate check

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

        # Check for duplicates (O(E) operation)
        if self.has_edge(edge.source, edge.target):
            msg = f"Edge {edge.source!r} -> {edge.target!r} already exists"
            raise ValueError(msg)

        self._edges.append(edge)

    def remove_vertex(self, vertex_id: Any) -> None:
        """
        Remove vertex and all incident edges.

        Time Complexity: O(E)

        Args:
            vertex_id: Identifier of vertex to remove

        Raises:
            KeyError: If vertex doesn't exist
        """
        if vertex_id not in self._vertices:
            msg = f"Vertex {vertex_id!r} not found"
            raise KeyError(msg)

        # Remove all incident edges
        self._edges = [
            e for e in self._edges 
            if e.source != vertex_id and e.target != vertex_id
        ]
        
        # Remove vertex
        del self._vertices[vertex_id]

    def remove_edge(self, source: Any, target: Any) -> None:
        """
        Remove edge from the representation.

        Time Complexity: O(E)

        Args:
            source: Source vertex identifier
            target: Target vertex identifier

        Raises:
            KeyError: If edge doesn't exist
        """
        # Find and remove the edge
        for i, edge in enumerate(self._edges):
            if edge.source == source and edge.target == target:
                del self._edges[i]
                return
            # For undirected graphs, check reverse direction
            if not self._directed and edge.source == target and edge.target == source:
                del self._edges[i]
                return

        msg = f"Edge {source!r} -> {target!r} not found"
        raise KeyError(msg)

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

        Time Complexity: O(E) - Linear scan through edges

        Args:
            source: Source vertex identifier
            target: Target vertex identifier

        Returns:
            True if edge exists
        """
        for edge in self._edges:
            if edge.source == source and edge.target == target:
                return True
            # For undirected graphs, check both directions
            if not self._directed and edge.source == target and edge.target == source:
                return True
        return False

    def get_neighbors(self, vertex_id: Any) -> set[Any]:
        """
        Get neighbors of a vertex.

        Time Complexity: O(E) - Must scan all edges

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

        neighbors = set()
        for edge in self._edges:
            if edge.source == vertex_id:
                neighbors.add(edge.target)
            elif not self._directed and edge.target == vertex_id:
                neighbors.add(edge.source)
        
        return neighbors

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

        Time Complexity: O(E)

        Args:
            source: Source vertex identifier
            target: Target vertex identifier

        Returns:
            Edge object

        Raises:
            KeyError: If edge doesn't exist
        """
        for edge in self._edges:
            if edge.source == source and edge.target == target:
                return edge
            if not self._directed and edge.source == target and edge.target == source:
                return edge
        
        msg = f"Edge {source!r} -> {target!r} not found"
        raise KeyError(msg)

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

        Yields:
            Edge objects
        """
        yield from self._edges

    def vertex_count(self) -> int:
        """
        Get total number of vertices.

        Returns:
            Number of vertices
        """
        return len(self._vertices)

    def edge_count(self) -> int:
        """
        Get total number of edges.

        Returns:
            Number of edges
        """
        return len(self._edges)

    def clear(self) -> None:
        """Remove all vertices and edges."""
        self._vertices.clear()
        self._edges.clear()

    def to_list(self) -> list[tuple[Any, Any, float]]:
        """
        Export edges as simple list of tuples.

        Returns:
            List of (source, target, weight) tuples

        Examples:
            >>> repr.to_list()
            [('A', 'B', 5.0), ('B', 'C', 3.0)]
        """
        return [(e.source, e.target, e.weight) for e in self._edges]

    def __repr__(self) -> str:
        """String representation for debugging."""
        return (
            f"EdgeListRepresentation("
            f"vertices={self.vertex_count()}, "
            f"edges={self.edge_count()}, "
            f"directed={self._directed})"
        )


def to_edge_list(graph: Any) -> list[dict[str, Any]]:
    """
    Convert graph to edge list format (list of dicts).

    Args:
        graph: Source graph

    Returns:
        List of dictionaries with edge data (source, target, weight, attributes...)
    """
    edge_list = []
    
    for edge in graph.edges():
        edge_data = {
            "source": edge.source,
            "target": edge.target,
            "weight": edge.weight,
            **edge.attributes
        }
        edge_list.append(edge_data)
        
    return edge_list
