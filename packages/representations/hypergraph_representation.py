"""Hypergraph representation using incidence list structure.

Hypergraphs generalize graphs by allowing edges (hyperedges) to connect
arbitrary sets of vertices, not just pairs.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Iterable
from uuid import uuid4

from packages.representations.base_representation import GraphRepresentation

if TYPE_CHECKING:
    from packages.core.edge import Edge
    from packages.core.vertex import Vertex, VertexId


class HypergraphRepresentation(GraphRepresentation):
    """Hypergraph representation using incidence list approach.

    In a hypergraph, an edge (hyperedge) can connect any number of vertices,
    not just two. This implementation uses an incidence list structure where
    we track which edges each vertex participates in, and which vertices
    each edge connects.

    Data Structure:
        - _vertex_to_edges: dict[VertexId, set[EdgeId]] - Which edges include each vertex
        - _edge_to_vertices: dict[EdgeId, frozenset[VertexId]] - Which vertices each edge connects
        - _edge_objects: dict[EdgeId, Edge] - The actual edge objects
        - _vertices: set[VertexId] - Set of all vertices for O(1) membership checks

    Edge Representation:
        For compatibility with the Graph contract, hyperedges are stored as
        Edge objects with:
        - source: arbitrary vertex from the hyperedge
        - target: arbitrary vertex from the hyperedge
        - attributes: {'hyperedge_vertices': frozenset[VertexId]}

    Performance Characteristics:
        - has_edge: O(1) average (check if edge ID exists)
        - get_neighbors: O(k * m) where k is edges per vertex, m is vertices per edge
        - add_edge: O(n) where n is number of vertices in the hyperedge
        - remove_edge: O(n) where n is number of vertices in the hyperedge

    Limitations:
        - get_edge and get_all_edges work for 2-vertex hyperedges (degenerate case)
        - For true hypergraphs, use get_hyperedge and query by edge ID

    Examples:
        >>> repr = HypergraphRepresentation()
        >>> repr.add_vertex(Vertex(id="A"))
        >>> repr.add_vertex(Vertex(id="B"))
        >>> repr.add_vertex(Vertex(id="C"))
        >>> # Add hyperedge connecting three vertices
        >>> edge = Edge(
        ...     source="A",
        ...     target="B",
        ...     attributes={'hyperedge_vertices': frozenset(['A', 'B', 'C'])}
        ... )
        >>> repr.add_edge(edge)
        >>> # All three vertices are now neighbors
        >>> set(repr.get_neighbors("A"))
        {'B', 'C'}
    """

    __slots__ = ("_vertex_to_edges", "_edge_to_vertices", "_edge_objects", "_vertices")

    def __init__(self) -> None:
        """Initialize an empty hypergraph."""
        self._vertex_to_edges: dict[VertexId, set[str]] = {}
        self._edge_to_vertices: dict[str, frozenset[VertexId]] = {}
        self._edge_objects: dict[str, Edge[VertexId]] = {}
        self._vertices: set[VertexId] = set()

    def add_vertex(self, vertex: Vertex[VertexId]) -> None:
        """Add a vertex to the hypergraph (idempotent).

        Args:
            vertex: Validated Vertex instance

        Time Complexity:
            O(1) amortized
        """
        if vertex.id not in self._vertices:
            self._vertices.add(vertex.id)
            self._vertex_to_edges[vertex.id] = set()

    def remove_vertex(self, vertex_id: VertexId) -> None:
        """Remove a vertex and all incident hyperedges.

        Args:
            vertex_id: Vertex identifier to remove

        Raises:
            KeyError: If vertex does not exist

        Time Complexity:
            O(k * n) where k is edges per vertex, n is vertices per edge
        """
        if vertex_id not in self._vertices:
            msg = f"Vertex {vertex_id!r} does not exist"
            raise KeyError(msg)

        # Remove all hyperedges containing this vertex
        edge_ids = list(self._vertex_to_edges[vertex_id])
        for edge_id in edge_ids:
            self._remove_hyperedge_by_id(edge_id)

        # Remove vertex
        del self._vertex_to_edges[vertex_id]
        self._vertices.remove(vertex_id)

    def add_edge(self, edge: Edge[VertexId]) -> None:
        """Add a hyperedge connecting multiple vertices.

        The edge's attributes should contain 'hyperedge_vertices' with a
        frozenset of all vertices in the hyperedge. If not provided,
        defaults to a 2-vertex hyperedge (source, target).

        Args:
            edge: Edge object with hyperedge_vertices in attributes

        Raises:
            ValueError: If any vertex in the hyperedge does not exist

        Time Complexity:
            O(n) where n is number of vertices in the hyperedge
        """
        # Extract hyperedge vertices from attributes
        hyperedge_vertices = edge.attributes.get(
            'hyperedge_vertices',
            frozenset([edge.source, edge.target]),
        )

        if not isinstance(hyperedge_vertices, frozenset):
            hyperedge_vertices = frozenset(hyperedge_vertices)

        # Validate all vertices exist
        for vertex_id in hyperedge_vertices:
            if vertex_id not in self._vertices:
                msg = f"Vertex {vertex_id!r} does not exist"
                raise ValueError(msg)

        # Generate unique edge ID
        edge_id = str(uuid4())

        # Store edge
        self._edge_to_vertices[edge_id] = hyperedge_vertices
        self._edge_objects[edge_id] = edge

        # Update vertex incidence lists
        for vertex_id in hyperedge_vertices:
            self._vertex_to_edges[vertex_id].add(edge_id)

    def remove_edge(self, source: VertexId, target: VertexId) -> None:
        """Remove hyperedges connecting exactly source and target.

        For true hypergraphs with 3+ vertices per edge, this only removes
        degenerate 2-vertex hyperedges. Use remove_hyperedge_by_id for
        general hyperedge removal.

        Args:
            source: Source vertex identifier
            target: Target vertex identifier

        Raises:
            ValueError: If no such hyperedge exists

        Time Complexity:
            O(k) where k is number of edges containing source
        """
        target_set = frozenset([source, target])
        edge_id = None

        # Find edge with exactly these two vertices
        if source in self._vertex_to_edges:
            for eid in self._vertex_to_edges[source]:
                if self._edge_to_vertices[eid] == target_set:
                    edge_id = eid
                    break

        if edge_id is None:
            msg = f"No hyperedge connecting exactly {source!r} and {target!r}"
            raise ValueError(msg)

        self._remove_hyperedge_by_id(edge_id)

    def has_edge(self, source: VertexId, target: VertexId) -> bool:
        """Check if a hyperedge connects exactly source and target.

        Args:
            source: Source vertex identifier
            target: Target vertex identifier

        Returns:
            True if a 2-vertex hyperedge exists, False otherwise

        Time Complexity:
            O(k) where k is number of edges containing source
        """
        if source not in self._vertex_to_edges:
            return False

        target_set = frozenset([source, target])
        return any(
            self._edge_to_vertices[eid] == target_set
            for eid in self._vertex_to_edges[source]
        )

    def get_edge(self, source: VertexId, target: VertexId) -> Edge[VertexId]:
        """Retrieve a hyperedge connecting exactly source and target.

        Args:
            source: Source vertex identifier
            target: Target vertex identifier

        Returns:
            Edge object

        Raises:
            ValueError: If no such hyperedge exists

        Time Complexity:
            O(k) where k is number of edges containing source
        """
        if source not in self._vertex_to_edges:
            msg = f"No hyperedge connecting {source!r} and {target!r}"
            raise ValueError(msg)

        target_set = frozenset([source, target])
        for eid in self._vertex_to_edges[source]:
            if self._edge_to_vertices[eid] == target_set:
                return self._edge_objects[eid]

        msg = f"No hyperedge connecting {source!r} and {target!r}"
        raise ValueError(msg)

    def get_all_edges(
        self,
        source: VertexId,
        target: VertexId,
    ) -> list[Edge[VertexId]]:
        """Retrieve all hyperedges connecting exactly source and target.

        Args:
            source: Source vertex identifier
            target: Target vertex identifier

        Returns:
            List of Edge objects (empty if none exist)

        Time Complexity:
            O(k) where k is number of edges containing source
        """
        if source not in self._vertex_to_edges:
            return []

        target_set = frozenset([source, target])
        return [
            self._edge_objects[eid]
            for eid in self._vertex_to_edges[source]
            if self._edge_to_vertices[eid] == target_set
        ]

    def get_neighbors(self, vertex_id: VertexId) -> Iterable[VertexId]:
        """Get all vertices connected via hyperedges.

        A vertex is a neighbor if it shares at least one hyperedge with
        the given vertex.

        Args:
            vertex_id: Vertex identifier

        Returns:
            Set of unique neighbor vertex identifiers

        Raises:
            KeyError: If vertex does not exist

        Time Complexity:
            O(k * m) where k is edges per vertex, m is vertices per edge
        """
        if vertex_id not in self._vertices:
            msg = f"Vertex {vertex_id!r} does not exist"
            raise KeyError(msg)

        neighbors: set[VertexId] = set()
        for edge_id in self._vertex_to_edges[vertex_id]:
            vertices = self._edge_to_vertices[edge_id]
            neighbors.update(vertices)

        # Remove the vertex itself
        neighbors.discard(vertex_id)
        return neighbors

    def vertex_count(self) -> int:
        """Get vertex count (O(1))."""
        return len(self._vertices)

    def edge_count(self) -> int:
        """Get hyperedge count (O(1))."""
        return len(self._edge_objects)

    def _remove_hyperedge_by_id(self, edge_id: str) -> None:
        """Internal method to remove a hyperedge by ID.

        Args:
            edge_id: Unique hyperedge identifier
        """
        if edge_id not in self._edge_objects:
            return

        # Remove from vertex incidence lists
        vertices = self._edge_to_vertices[edge_id]
        for vertex_id in vertices:
            if vertex_id in self._vertex_to_edges:
                self._vertex_to_edges[vertex_id].discard(edge_id)

        # Remove edge data
        del self._edge_to_vertices[edge_id]
        del self._edge_objects[edge_id]

    def get_hyperedge(self, edge_id: str) -> tuple[frozenset[VertexId], Edge[VertexId]]:
        """Get hyperedge by ID (useful for true hypergraph operations).

        Args:
            edge_id: Unique hyperedge identifier

        Returns:
            Tuple of (vertices in hyperedge, Edge object)

        Raises:
            KeyError: If edge ID does not exist
        """
        if edge_id not in self._edge_objects:
            msg = f"Hyperedge {edge_id!r} does not exist"
            raise KeyError(msg)
        return self._edge_to_vertices[edge_id], self._edge_objects[edge_id]
