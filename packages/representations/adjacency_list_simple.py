"""Simple graph adjacency list representation (set-based).

Optimized for graphs without multi-edges (parallel edges). Uses set for O(1)
neighbor lookups and separate dict for edge storage.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Iterable

from packages.representations.base_representation import GraphRepresentation

if TYPE_CHECKING:
    from collections.abc import Iterator

    from packages.core.edge import Edge
    from packages.core.vertex import Vertex, VertexId


class SimpleAdjacencyListRepresentation(GraphRepresentation):
    """Adjacency list for simple graphs (no multi-edges)."""

    __slots__ = ("_adjacency", "_edges", "_edge_count", "_vertices_store")

    def __init__(self) -> None:
        """Initialize an empty simple adjacency list."""
        self._adjacency: dict[VertexId, set[VertexId]] = {}
        self._edges: dict[tuple[VertexId, VertexId], Edge[VertexId]] = {}
        self._edge_count: int = 0
        self._vertices_store: dict[VertexId, Vertex[VertexId]] = {}

    def add_vertex(self, vertex: Vertex[VertexId]) -> None:
        """Add a vertex to the graph (idempotent)."""
        if vertex.id not in self._adjacency:
            self._adjacency[vertex.id] = set()
        # Always update vertex data in case attributes changed
        self._vertices_store[vertex.id] = vertex

    def remove_vertex(self, vertex_id: VertexId) -> None:
        """Remove a vertex and all incident edges."""
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
        del self._vertices_store[vertex_id]

    def add_edge(self, edge: Edge[VertexId]) -> None:
        """Add an edge to the graph."""
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
        """Remove an edge from the graph."""
        self._remove_edge_internal(source, target)

    def _remove_edge_internal(self, source: VertexId, target: VertexId) -> None:
        """Internal method to remove edge."""
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
            # Should not happen if consistency is maintained
            pass

        # Remove from adjacency structure
        self._adjacency[source].discard(target)

        if edge and not edge.directed:
            self._adjacency[target].discard(source)

        # Remove edge object
        actual_key = edge_key_directed if edge_key_directed in self._edges else edge_key_undirected
        if actual_key in self._edges:
            del self._edges[actual_key]
            self._edge_count -= 1

    def has_edge(self, source: VertexId, target: VertexId) -> bool:
        """Check if an edge exists."""
        return source in self._adjacency and target in self._adjacency[source]

    def get_edge(self, source: VertexId, target: VertexId) -> Edge[VertexId]:
        """Retrieve a single edge."""
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
        """Retrieve all edges (returns list of 0 or 1 element)."""
        try:
            return [self.get_edge(source, target)]
        except ValueError:
            return []

    def get_neighbors(self, vertex_id: VertexId) -> Iterable[VertexId]:
        """Get all neighbors."""
        if vertex_id not in self._adjacency:
            msg = f"Vertex {vertex_id!r} does not exist"
            raise KeyError(msg)
        return self._adjacency[vertex_id]

    def vertex_count(self) -> int:
        """Get vertex count."""
        return len(self._adjacency)

    def edge_count(self) -> int:
        """Get edge count."""
        return self._edge_count

    # --- New methods required by SimpleGraph ---

    def has_vertex(self, vertex_id: VertexId) -> bool:
        """Check if vertex exists."""
        return vertex_id in self._vertices_store

    def get_vertex(self, vertex_id: VertexId) -> Vertex[VertexId]:
        """Get vertex object."""
        if vertex_id not in self._vertices_store:
            msg = f"Vertex {vertex_id!r} does not exist"
            raise KeyError(msg)
        return self._vertices_store[vertex_id]

    def vertices(self) -> Iterator[Vertex[VertexId]]:
        """Iterate over all vertices."""
        yield from self._vertices_store.values()

    def edges(self) -> Iterator[Edge[VertexId]]:
        """Iterate over all edges."""
        yield from self._edges.values()

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
