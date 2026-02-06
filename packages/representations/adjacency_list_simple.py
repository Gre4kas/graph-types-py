"""Simple graph adjacency list representation (set-based).

Optimized for graphs without multi-edges (parallel edges). Uses set for O(1)
neighbor lookups and separate dict for edge storage.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Iterable

from packages.representations.base_representation import GraphRepresentation

if TYPE_CHECKING:
    from packages.core.edge import Edge
    from packages.core.vertex import Vertex, VertexId


class SimpleAdjacencyListRepresentation(GraphRepresentation):
    """Adjacency list for simple graphs (no multi-edges).

    This implementation uses a set-based adjacency structure for maximum speed
    in neighbor lookups and edge existence checks. It is optimized for simple
    graphs where duplicate edges are not allowed.

    Data Structure:
        - _adjacency: dict[VertexId, set[VertexId]] - Fast neighbor lookups
        - _edges: dict[tuple[VertexId, VertexId], Edge] - Edge object storage
        - _edge_count: int - Cached edge count for O(1) access

    Performance Characteristics:
        - has_edge: O(1) average via set membership
        - get_neighbors: O(1) to get set, O(k) to iterate k neighbors
        - add_edge: O(1) average
        - remove_edge: O(1) average

    Memory:
        Uses __slots__ to minimize overhead. Approximately 64 bytes per vertex
        + 16 bytes per edge (set element) + edge object size.

    Thread Safety:
        Not thread-safe. External synchronization required.

    Examples:
        >>> repr = SimpleAdjacencyListRepresentation()
        >>> repr.add_vertex(Vertex(id="A"))
        >>> repr.add_vertex(Vertex(id="B"))
        >>> repr.add_edge(Edge(source="A", target="B", weight=5.0))
        >>> repr.has_edge("A", "B")
        True
        >>> repr.add_edge(Edge(source="A", target="B"))  # Raises ValueError
    """

    __slots__ = ("_adjacency", "_edges", "_edge_count")

    def __init__(self) -> None:
        """Initialize an empty simple adjacency list."""
        self._adjacency: dict[VertexId, set[VertexId]] = {}
        self._edges: dict[tuple[VertexId, VertexId], Edge[VertexId]] = {}
        self._edge_count: int = 0

    def add_vertex(self, vertex: Vertex[VertexId]) -> None:
        """Add a vertex to the graph (idempotent).

        Args:
            vertex: Validated Vertex instance

        Time Complexity:
            O(1) amortized
        """
        if vertex.id not in self._adjacency:
            self._adjacency[vertex.id] = set()

    def remove_vertex(self, vertex_id: VertexId) -> None:
        """Remove a vertex and all incident edges.

        Args:
            vertex_id: Vertex identifier to remove

        Raises:
            KeyError: If vertex does not exist

        Time Complexity:
            O(V + E) worst case
        """
        if vertex_id not in self._adjacency:
            msg = f"Vertex {vertex_id!r} does not exist"
            raise KeyError(msg)

        # Remove all edges incident to this vertex
        neighbors = list(self._adjacency[vertex_id])
        for neighbor in neighbors:
            self._remove_edge_internal(vertex_id, neighbor)

        # Remove edges where this vertex is the target
        for source in list(self._adjacency.keys()):
            if vertex_id in self._adjacency[source]:
                self._remove_edge_internal(source, vertex_id)

        # Remove the vertex itself
        del self._adjacency[vertex_id]

    def add_edge(self, edge: Edge[VertexId]) -> None:
        """Add an edge to the graph.

        Args:
            edge: Validated Edge instance

        Raises:
            ValueError: If source or target vertex does not exist
            ValueError: If edge already exists (no duplicates allowed)

        Time Complexity:
            O(1) amortized
        """
        if edge.source not in self._adjacency:
            msg = f"Source vertex {edge.source!r} does not exist"
            raise ValueError(msg)
        if edge.target not in self._adjacency:
            msg = f"Target vertex {edge.target!r} does not exist"
            raise ValueError(msg)

        # Check for duplicate edge
        if edge.target in self._adjacency[edge.source]:
            msg = f"Edge {edge.source!r} -> {edge.target!r} already exists"
            raise ValueError(msg)

        # Add edge to adjacency structure
        self._adjacency[edge.source].add(edge.target)

        # For undirected edges, add reverse direction
        if not edge.directed:
            self._adjacency[edge.target].add(edge.source)

        # Store edge object
        edge_key = self._make_edge_key(edge.source, edge.target, edge.directed)
        self._edges[edge_key] = edge
        self._edge_count += 1

    def remove_edge(self, source: VertexId, target: VertexId) -> None:
        """Remove an edge from the graph.

        Args:
            source: Source vertex identifier
            target: Target vertex identifier

        Raises:
            ValueError: If edge does not exist

        Time Complexity:
            O(1) amortized
        """
        self._remove_edge_internal(source, target)

    def _remove_edge_internal(self, source: VertexId, target: VertexId) -> None:
        """Internal method to remove edge (used by remove_vertex)."""
        if source not in self._adjacency or target not in self._adjacency[source]:
            msg = f"Edge {source!r} -> {target!r} does not exist"
            raise ValueError(msg)

        # Try directed key first
        edge_key_directed = (source, target)
        edge_key_undirected = self._normalize_edge_key(source, target)

        edge = self._edges.get(edge_key_directed) or self._edges.get(
            edge_key_undirected,
        )

        if edge is None:
            msg = f"Edge {source!r} -> {target!r} does not exist in edge storage"
            raise ValueError(msg)

        # Remove from adjacency structure
        self._adjacency[source].discard(target)

        # For undirected edges, remove reverse direction
        if not edge.directed:
            self._adjacency[target].discard(source)

        # Remove edge object
        actual_key = edge_key_directed if edge_key_directed in self._edges else edge_key_undirected
        del self._edges[actual_key]
        self._edge_count -= 1

    def has_edge(self, source: VertexId, target: VertexId) -> bool:
        """Check if an edge exists (O(1) average).

        Args:
            source: Source vertex identifier
            target: Target vertex identifier

        Returns:
            True if edge exists, False otherwise
        """
        return source in self._adjacency and target in self._adjacency[source]

    def get_edge(self, source: VertexId, target: VertexId) -> Edge[VertexId]:
        """Retrieve a single edge.

        Args:
            source: Source vertex identifier
            target: Target vertex identifier

        Returns:
            Edge object

        Raises:
            ValueError: If edge does not exist

        Time Complexity:
            O(1) amortized
        """
        # Try directed key
        edge = self._edges.get((source, target))
        if edge is not None:
            return edge

        # Try undirected key
        edge = self._edges.get(self._normalize_edge_key(source, target))
        if edge is not None:
            return edge

        msg = f"Edge {source!r} -> {target!r} does not exist"
        raise ValueError(msg)

    def get_all_edges(
        self,
        source: VertexId,
        target: VertexId,
    ) -> list[Edge[VertexId]]:
        """Retrieve all edges (returns list of 0 or 1 element for simple graphs).

        Args:
            source: Source vertex identifier
            target: Target vertex identifier

        Returns:
            List containing the edge, or empty list if no edge exists
        """
        try:
            return [self.get_edge(source, target)]
        except ValueError:
            return []

    def get_neighbors(self, vertex_id: VertexId) -> Iterable[VertexId]:
        """Get all neighbors (O(1) to get set).

        Args:
            vertex_id: Vertex identifier

        Returns:
            Set of neighbor vertex identifiers

        Raises:
            KeyError: If vertex does not exist
        """
        if vertex_id not in self._adjacency:
            msg = f"Vertex {vertex_id!r} does not exist"
            raise KeyError(msg)
        return self._adjacency[vertex_id]

    def vertex_count(self) -> int:
        """Get vertex count (O(1))."""
        return len(self._adjacency)

    def edge_count(self) -> int:
        """Get edge count (O(1))."""
        return self._edge_count

    @staticmethod
    def _make_edge_key(
        source: VertexId,
        target: VertexId,
        directed: bool,
    ) -> tuple[VertexId, VertexId]:
        """Create edge key for storage."""
        if directed:
            return (source, target)
        return (min(source, target), max(source, target))

    @staticmethod
    def _normalize_edge_key(
        source: VertexId,
        target: VertexId,
    ) -> tuple[VertexId, VertexId]:
        """Normalize edge key for undirected lookup."""
        return (min(source, target), max(source, target))
