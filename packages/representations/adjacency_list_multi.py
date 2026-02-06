"""Multigraph adjacency list representation (list-based)."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Iterable

from packages.representations.base_representation import GraphRepresentation

if TYPE_CHECKING:
    from collections.abc import Iterator

    from packages.core.edge import Edge
    from packages.core.vertex import Vertex, VertexId


class MultiAdjacencyListRepresentation(GraphRepresentation):
    """Adjacency list for multigraphs (supports parallel edges and loops)."""

    __slots__ = ("_adjacency", "_edge_count", "_vertices_store")

    def __init__(self) -> None:
        """Initialize an empty multigraph adjacency list."""
        self._adjacency: dict[VertexId, dict[VertexId, list[Edge[VertexId]]]] = {}
        self._edge_count: int = 0
        self._vertices_store: dict[VertexId, Vertex[VertexId]] = {}

    def add_vertex(self, vertex: Vertex[VertexId]) -> None:
        """Add a vertex to the multigraph (idempotent)."""
        if vertex.id not in self._adjacency:
            self._adjacency[vertex.id] = {}
        self._vertices_store[vertex.id] = vertex

    def remove_vertex(self, vertex_id: VertexId) -> None:
        """Remove a vertex and all incident edges."""
        if vertex_id not in self._adjacency:
            msg = f"Vertex {vertex_id!r} does not exist"
            raise KeyError(msg)

        # Count and remove edges where this vertex is the source
        outgoing = self._adjacency[vertex_id]
        for target, edges in outgoing.items():
            self._edge_count -= len(edges)
            for edge in edges:
                if not edge.directed and target != vertex_id:
                    # Remove from target's adjacency list
                    if target in self._adjacency:
                        target_neighbors = self._adjacency[target]
                        if vertex_id in target_neighbors:
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
                directed_edges = [e for e in edges if e.directed]
                self._edge_count -= len(directed_edges)
                del self._adjacency[source][vertex_id]

        del self._adjacency[vertex_id]
        del self._vertices_store[vertex_id]

    def add_edge(self, edge: Edge[VertexId]) -> None:
        """Add an edge to the multigraph (allows duplicates)."""
        if edge.source not in self._adjacency:
            msg = f"Source vertex {edge.source!r} does not exist"
            raise ValueError(msg)
        if edge.target not in self._adjacency:
            msg = f"Target vertex {edge.target!r} does not exist"
            raise ValueError(msg)

        if edge.target not in self._adjacency[edge.source]:
            self._adjacency[edge.source][edge.target] = []
        self._adjacency[edge.source][edge.target].append(edge)

        if not edge.directed:
            if edge.source not in self._adjacency[edge.target]:
                self._adjacency[edge.target][edge.source] = []
            if edge.source != edge.target:
                self._adjacency[edge.target][edge.source].append(edge)

        self._edge_count += 1

    def remove_edge(self, source: VertexId, target: VertexId) -> None:
        """Remove ALL edges between two vertices."""
        if source not in self._adjacency or target not in self._adjacency[source]:
            msg = f"No edge from {source!r} to {target!r}"
            raise ValueError(msg)

        edges = self._adjacency[source][target]
        if not edges:
            msg = f"No edge from {source!r} to {target!r}"
            raise ValueError(msg)

        edge_count = len(edges)
        is_directed = edges[0].directed

        del self._adjacency[source][target]

        if not is_directed and source != target:
            if target in self._adjacency and source in self._adjacency[target]:
                del self._adjacency[target][source]

        self._edge_count -= edge_count

    def has_edge(self, source: VertexId, target: VertexId) -> bool:
        """Check if at least one edge exists."""
        return (
            source in self._adjacency
            and target in self._adjacency[source]
            and len(self._adjacency[source][target]) > 0
        )

    def get_edge(self, source: VertexId, target: VertexId) -> Edge[VertexId]:
        """Retrieve an arbitrary edge (first in list)."""
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
        """Retrieve all parallel edges."""
        if source not in self._adjacency or target not in self._adjacency[source]:
            return []
        return self._adjacency[source][target].copy()

    def get_neighbors(self, vertex_id: VertexId) -> Iterable[VertexId]:
        """Get all unique neighbors."""
        if vertex_id not in self._adjacency:
            msg = f"Vertex {vertex_id!r} does not exist"
            raise KeyError(msg)
        return self._adjacency[vertex_id].keys()

    def vertex_count(self) -> int:
        """Get vertex count."""
        return len(self._adjacency)

    def edge_count(self) -> int:
        """Get total edge count."""
        return self._edge_count

    # --- New methods ---

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
        seen = set()
        for source_adj in self._adjacency.values():
            for edges_list in source_adj.values():
                for edge in edges_list:
                    # Avoid duplicates for undirected edges
                    if not edge.directed:
                        edge_key = tuple(sorted((edge.source, edge.target))) + (edge.weight,)
                        # Note: This simple dedupe might not handle all attribute cases perfectly
                        # but matches standard behavior. Using object identity is risky if rebuilt.
                        # Actually, edge objects are immutable.
                        if edge in seen:
                            continue
                        seen.add(edge)
                    yield edge

    @staticmethod
    def _edges_match(edge1: Edge[VertexId], edge2: Edge[VertexId]) -> bool:
        """Check if two edges are equivalent."""
        return (
            edge1.source == edge2.source
            and edge1.target == edge2.target
            and edge1.directed == edge2.directed
        )
