"""Hypergraph representation using incidence list structure."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Iterable
from uuid import uuid4

from packages.representations.base_representation import GraphRepresentation

if TYPE_CHECKING:
    from collections.abc import Iterator

    from packages.core.edge import Edge
    from packages.core.vertex import Vertex, VertexId


class HypergraphRepresentation(GraphRepresentation):
    """Hypergraph representation using incidence list approach."""

    __slots__ = ("_vertex_to_edges", "_edge_to_vertices", "_edge_objects", "_vertices_store")

    def __init__(self) -> None:
        """Initialize an empty hypergraph."""
        self._vertex_to_edges: dict[VertexId, set[str]] = {}
        self._edge_to_vertices: dict[str, frozenset[VertexId]] = {}
        self._edge_objects: dict[str, Edge[VertexId]] = {}
        self._vertices_store: dict[VertexId, Vertex[VertexId]] = {}

    def add_vertex(self, vertex: Vertex[VertexId]) -> None:
        """Add a vertex to the hypergraph (idempotent)."""
        if vertex.id not in self._vertices_store:
            self._vertex_to_edges[vertex.id] = set()
        self._vertices_store[vertex.id] = vertex

    def remove_vertex(self, vertex_id: VertexId) -> None:
        """Remove a vertex and all incident hyperedges."""
        if vertex_id not in self._vertices_store:
            msg = f"Vertex {vertex_id!r} does not exist"
            raise KeyError(msg)

        edge_ids = list(self._vertex_to_edges[vertex_id])
        for edge_id in edge_ids:
            self._remove_hyperedge_by_id(edge_id)

        del self._vertex_to_edges[vertex_id]
        del self._vertices_store[vertex_id]

    def add_edge(self, edge: Edge[VertexId]) -> None:
        """Add a hyperedge connecting multiple vertices."""
        hyperedge_vertices = edge.attributes.get(
            'hyperedge_vertices',
            frozenset([edge.source, edge.target]),
        )

        if not isinstance(hyperedge_vertices, frozenset):
            hyperedge_vertices = frozenset(hyperedge_vertices)

        for vertex_id in hyperedge_vertices:
            if vertex_id not in self._vertices_store:
                msg = f"Vertex {vertex_id!r} does not exist"
                raise ValueError(msg)

        edge_id = str(uuid4())
        self._edge_to_vertices[edge_id] = hyperedge_vertices
        self._edge_objects[edge_id] = edge

        for vertex_id in hyperedge_vertices:
            self._vertex_to_edges[vertex_id].add(edge_id)

    def remove_edge(self, source: VertexId, target: VertexId) -> None:
        """Remove hyperedges connecting exactly source and target."""
        target_set = frozenset([source, target])
        edge_id = None

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
        """Check if a hyperedge connects exactly source and target."""
        if source not in self._vertex_to_edges:
            return False

        target_set = frozenset([source, target])
        return any(
            self._edge_to_vertices[eid] == target_set
            for eid in self._vertex_to_edges[source]
        )

    def get_edge(self, source: VertexId, target: VertexId) -> Edge[VertexId]:
        """Retrieve a hyperedge connecting exactly source and target."""
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
        """Retrieve all hyperedges connecting exactly source and target."""
        if source not in self._vertex_to_edges:
            return []

        target_set = frozenset([source, target])
        return [
            self._edge_objects[eid]
            for eid in self._vertex_to_edges[source]
            if self._edge_to_vertices[eid] == target_set
        ]

    def get_neighbors(self, vertex_id: VertexId) -> Iterable[VertexId]:
        """Get all vertices connected via hyperedges."""
        if vertex_id not in self._vertices_store:
            msg = f"Vertex {vertex_id!r} does not exist"
            raise KeyError(msg)

        neighbors: set[VertexId] = set()
        for edge_id in self._vertex_to_edges[vertex_id]:
            vertices = self._edge_to_vertices[edge_id]
            neighbors.update(vertices)

        neighbors.discard(vertex_id)
        return neighbors

    def vertex_count(self) -> int:
        """Get vertex count."""
        return len(self._vertices_store)

    def edge_count(self) -> int:
        """Get hyperedge count."""
        return len(self._edge_objects)

    def _remove_hyperedge_by_id(self, edge_id: str) -> None:
        """Internal method to remove a hyperedge by ID."""
        if edge_id not in self._edge_objects:
            return

        vertices = self._edge_to_vertices[edge_id]
        for vertex_id in vertices:
            if vertex_id in self._vertex_to_edges:
                self._vertex_to_edges[vertex_id].discard(edge_id)

        del self._edge_to_vertices[edge_id]
        del self._edge_objects[edge_id]

    def get_hyperedge(self, edge_id: str) -> tuple[frozenset[VertexId], Edge[VertexId]]:
        """Get hyperedge by ID."""
        if edge_id not in self._edge_objects:
            msg = f"Hyperedge {edge_id!r} does not exist"
            raise KeyError(msg)
        return self._edge_to_vertices[edge_id], self._edge_objects[edge_id]

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
        yield from self._edge_objects.values()
