"""Multigraph adjacency list representation (list-based).

Optimized for graphs with multi-edges (parallel edges). Uses list to store
multiple edges between the same pair of vertices.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Iterable

from packages.representations.base_representation import GraphRepresentation

if TYPE_CHECKING:
    from packages.core.edge import Edge
    from packages.core.vertex import Vertex, VertexId


class MultiAdjacencyListRepresentation(GraphRepresentation):
    """Adjacency list for multigraphs (supports parallel edges and loops).

    This implementation uses a nested dict structure to store multiple edges
    between the same pair of vertices. It supports loops (self-edges) and
    parallel edges (multiple edges with same source and target).

    Data Structure:
        - _adjacency: dict[VertexId, dict[VertexId, list[Edge]]] - Nested structure
        - _edge_count: int - Cached total edge count

    Performance Characteristics:
        - has_edge: O(1) average (check if list exists and is non-empty)
        - get_neighbors: O(1) to get dict keys, returns unique neighbors
        - add_edge: O(1) average (append to list)
        - remove_edge: O(k) where k is number of parallel edges
        - get_all_edges: O(k) where k is number of parallel edges

    Memory:
        Uses __slots__ to minimize overhead. Higher memory usage than simple
        adjacency list due to nested dicts and edge lists.

    Thread Safety:
        Not thread-safe. External synchronization required.

    Examples:
        >>> repr = MultiAdjacencyListRepresentation()
        >>> repr.add_vertex(Vertex(id="A"))
        >>> repr.add_vertex(Vertex(id="B"))
        >>> # Add multiple edges between same vertices
        >>> repr.add_edge(Edge(source="A", target="B", weight=5.0))
        >>> repr.add_edge(Edge(source="A", target="B", weight=10.0))
        >>> len(repr.get_all_edges("A", "B"))
        2
        >>> # Self-loop support
        >>> repr.add_edge(Edge(source="A", target="A", weight=1.0))
    """

    __slots__ = ("_adjacency", "_edge_count")

    def __init__(self) -> None:
        """Initialize an empty multigraph adjacency list."""
        self._adjacency: dict[VertexId, dict[VertexId, list[Edge[VertexId]]]] = {}
        self._edge_count: int = 0

    def add_vertex(self, vertex: Vertex[VertexId]) -> None:
        """Add a vertex to the multigraph (idempotent).

        Args:
            vertex: Validated Vertex instance

        Time Complexity:
            O(1) amortized
        """
        if vertex.id not in self._adjacency:
            self._adjacency[vertex.id] = {}

    def remove_vertex(self, vertex_id: VertexId) -> None:
        """Remove a vertex and all incident edges.

        Args:
            vertex_id: Vertex identifier to remove

        Raises:
            KeyError: If vertex does not exist

        Time Complexity:
            O(V * E) worst case (must check all adjacency lists)
        """
        if vertex_id not in self._adjacency:
            msg = f"Vertex {vertex_id!r} does not exist"
            raise KeyError(msg)

        # Count and remove edges where this vertex is the source
        outgoing = self._adjacency[vertex_id]
        for target, edges in outgoing.items():
            self._edge_count -= len(edges)

            # For undirected edges, remove reverse references
            for edge in edges:
                if not edge.directed and target != vertex_id:
                    # Remove from target's adjacency list
                    if target in self._adjacency:
                        target_neighbors = self._adjacency[target]
                        if vertex_id in target_neighbors:
                            # Find and remove the corresponding edge
                            target_neighbors[vertex_id] = [
                                e
                                for e in target_neighbors[vertex_id]
                                if not self._edges_match(e, edge)
                            ]
                            if not target_neighbors[vertex_id]:
                                del target_neighbors[vertex_id]

        # Remove edges where this vertex is the target (for directed graphs)
        for source in list(self._adjacency.keys()):
            if source != vertex_id and vertex_id in self._adjacency[source]:
                edges = self._adjacency[source][vertex_id]
                # Only count directed edges (undirected were counted above)
                directed_edges = [e for e in edges if e.directed]
                self._edge_count -= len(directed_edges)
                del self._adjacency[source][vertex_id]

        # Remove the vertex itself
        del self._adjacency[vertex_id]

    def add_edge(self, edge: Edge[VertexId]) -> None:
        """Add an edge to the multigraph (allows duplicates).

        Args:
            edge: Validated Edge instance

        Raises:
            ValueError: If source or target vertex does not exist

        Time Complexity:
            O(1) amortized
        """
        if edge.source not in self._adjacency:
            msg = f"Source vertex {edge.source!r} does not exist"
            raise ValueError(msg)
        if edge.target not in self._adjacency:
            msg = f"Target vertex {edge.target!r} does not exist"
            raise ValueError(msg)

        # Add edge to source's adjacency list
        if edge.target not in self._adjacency[edge.source]:
            self._adjacency[edge.source][edge.target] = []
        self._adjacency[edge.source][edge.target].append(edge)

        # For undirected edges, add reverse direction
        if not edge.directed:
            if edge.source not in self._adjacency[edge.target]:
                self._adjacency[edge.target][edge.source] = []
            # Don't add duplicate for self-loops
            if edge.source != edge.target:
                self._adjacency[edge.target][edge.source].append(edge)

        self._edge_count += 1

    def remove_edge(self, source: VertexId, target: VertexId) -> None:
        """Remove ALL edges between two vertices.

        Args:
            source: Source vertex identifier
            target: Target vertex identifier

        Raises:
            ValueError: If no edge exists

        Time Complexity:
            O(k) where k is number of parallel edges
        """
        if source not in self._adjacency or target not in self._adjacency[source]:
            msg = f"No edge from {source!r} to {target!r}"
            raise ValueError(msg)

        edges = self._adjacency[source][target]
        if not edges:
            msg = f"No edge from {source!r} to {target!r}"
            raise ValueError(msg)

        edge_count = len(edges)
        is_directed = edges[0].directed

        # Remove from source adjacency
        del self._adjacency[source][target]

        # For undirected edges, remove reverse direction
        if not is_directed and source != target:
            if target in self._adjacency and source in self._adjacency[target]:
                del self._adjacency[target][source]

        self._edge_count -= edge_count

    def has_edge(self, source: VertexId, target: VertexId) -> bool:
        """Check if at least one edge exists (O(1) average).

        Args:
            source: Source vertex identifier
            target: Target vertex identifier

        Returns:
            True if at least one edge exists, False otherwise
        """
        return (
            source in self._adjacency
            and target in self._adjacency[source]
            and len(self._adjacency[source][target]) > 0
        )

    def get_edge(self, source: VertexId, target: VertexId) -> Edge[VertexId]:
        """Retrieve an arbitrary edge (first in list for multigraphs).

        Args:
            source: Source vertex identifier
            target: Target vertex identifier

        Returns:
            First Edge object in the list

        Raises:
            ValueError: If no edge exists

        Time Complexity:
            O(1) amortized
        """
        edges = self.get_all_edges(source, target)
        if not edges:
            msg = f"No edge from {source!r} to {target!r}"
            raise ValueError(msg)
        return edges[0]

    def get_all_edges(
        self,
        source: VertexId,
        target: VertexId,
    ) -> list[Edge[VertexId]]:
        """Retrieve all parallel edges between two vertices.

        Args:
            source: Source vertex identifier
            target: Target vertex identifier

        Returns:
            List of all Edge objects (empty if no edges exist)

        Time Complexity:
            O(k) where k is number of parallel edges
        """
        if source not in self._adjacency or target not in self._adjacency[source]:
            return []
        return self._adjacency[source][target].copy()

    def get_neighbors(self, vertex_id: VertexId) -> Iterable[VertexId]:
        """Get all unique neighbors (O(1) to get keys).

        For multigraphs, each neighbor appears only once even if multiple
        edges connect them.

        Args:
            vertex_id: Vertex identifier

        Returns:
            Dict keys view of unique neighbor vertex identifiers

        Raises:
            KeyError: If vertex does not exist
        """
        if vertex_id not in self._adjacency:
            msg = f"Vertex {vertex_id!r} does not exist"
            raise KeyError(msg)
        return self._adjacency[vertex_id].keys()

    def vertex_count(self) -> int:
        """Get vertex count (O(1))."""
        return len(self._adjacency)

    def edge_count(self) -> int:
        """Get total edge count including parallel edges (O(1))."""
        return self._edge_count

    @staticmethod
    def _edges_match(edge1: Edge[VertexId], edge2: Edge[VertexId]) -> bool:
        """Check if two edges are equivalent (for undirected edge removal)."""
        return (
            edge1.source == edge2.source
            and edge1.target == edge2.target
            and edge1.directed == edge2.directed
        )
