"""
Hypergraph implementation (edges connect arbitrary number of vertices).

Mathematical definition: H = (V, E) where E is a family of non-empty
subsets of V. Unlike simple graphs, hyperedges can connect any number
of vertices (not just pairs).
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from packages.core.base_graph import BaseGraph
from packages.core.vertex import Vertex
from packages.representations.base_representation import GraphRepresentation
from packages.utils.exceptions import GraphConstraintError, VertexNotFoundError
from packages.utils.validators import validate_hyperedge_vertices

if TYPE_CHECKING:
    from collections.abc import Iterator


class Hyperedge:
    """
    Represents a hyperedge connecting multiple vertices.

    Attributes:
        vertices: Set of vertex identifiers in this hyperedge
        weight: Hyperedge weight (default: 1.0)
        attributes: Arbitrary metadata

    Examples:
        >>> he = Hyperedge({"A", "B", "C"}, weight=5.0)
        >>> he.size()
        3
        >>> "A" in he
        True
    """

    __slots__ = ("vertices", "weight", "attributes", "_hash_cache")

    def __init__(
        self,
        vertices: set[Any],
        *,
        weight: float = 1.0,
        **attributes: Any,
    ) -> None:
        """
        Initialize hyperedge.

        Args:
            vertices: Set of vertex identifiers (must have ≥2 vertices)
            weight: Hyperedge weight
            **attributes: Arbitrary metadata

        Raises:
            ValueError: If vertices set has less than 2 elements
        """
        self.vertices = validate_hyperedge_vertices(vertices)
        self.weight = weight
        self.attributes = attributes

    def size(self) -> int:
        """Get number of vertices in this hyperedge."""
        return len(self.vertices)

    def is_incident_to(self, vertex_id: Any) -> bool:
        """Check if hyperedge is incident to a vertex."""
        return vertex_id in self.vertices

    def __contains__(self, vertex_id: Any) -> bool:
        """Check if vertex is in hyperedge."""
        return vertex_id in self.vertices

    def __getitem__(self, key: str) -> Any:
        """Allow dictionary-like access to attributes."""
        if hasattr(self, key):
            return getattr(self, key)
        if key in self.attributes:
            return self.attributes[key]
        raise KeyError(f"Key {key!r} not found in Hyperedge")

    def __hash__(self) -> int:
        """Hash based on frozenset of vertices."""
        if not hasattr(self, "_hash_cache"):
            object.__setattr__(self, "_hash_cache", hash(frozenset(self.vertices)))
        return self._hash_cache

    def __eq__(self, other: object) -> bool:
        """Equality based on vertex set."""
        if not isinstance(other, Hyperedge):
            return NotImplemented
        return self.vertices == other.vertices

    def __repr__(self) -> str:
        """String representation."""
        vertices_str = ", ".join(sorted(str(v) for v in self.vertices))
        return f"Hyperedge({{{vertices_str}}})"


class HypergraphRepresentation(GraphRepresentation):
    """
    Specialized representation for hypergraphs.

    Stores hyperedges as sets of vertices with arbitrary cardinality.
    """

    __slots__ = ("_vertices", "_hyperedges", "_incidence", "_edge_counter")

    def __init__(self) -> None:
        """Initialize hypergraph representation."""
        self._vertices: dict[Any, Vertex] = {}
        self._hyperedges: dict[int, Hyperedge] = {}
        self._incidence: dict[Any, set[int]] = {}  # vertex -> hyperedge IDs
        self._edge_counter = 0

    def add_vertex(self, vertex: Vertex) -> None:
        """Add vertex to hypergraph."""
        if vertex.id in self._vertices:
            msg = f"Vertex {vertex.id!r} already exists"
            raise ValueError(msg)
        self._vertices[vertex.id] = vertex
        self._incidence[vertex.id] = set()

    def add_hyperedge(self, hyperedge: Hyperedge) -> int:
        """
        Add hyperedge to hypergraph.

        Args:
            hyperedge: Hyperedge object

        Returns:
            Unique hyperedge identifier

        Raises:
            KeyError: If any vertex in hyperedge doesn't exist
        """
        # Validate all vertices exist
        for vid in hyperedge.vertices:
            if vid not in self._vertices:
                msg = f"Vertex {vid!r} not found"
                raise KeyError(msg)

        # Assign unique ID
        edge_id = self._edge_counter
        self._edge_counter += 1

        # Store hyperedge
        self._hyperedges[edge_id] = hyperedge

        # Update incidence
        for vid in hyperedge.vertices:
            self._incidence[vid].add(edge_id)

        return edge_id

    def remove_vertex(self, vertex_id: Any) -> None:
        """Remove vertex and all incident hyperedges."""
        if vertex_id not in self._vertices:
            msg = f"Vertex {vertex_id!r} not found"
            raise KeyError(msg)

        # Remove all incident hyperedges
        incident_edges = list(self._incidence[vertex_id])
        for edge_id in incident_edges:
            self.remove_hyperedge(edge_id)

        # Remove vertex
        del self._vertices[vertex_id]
        del self._incidence[vertex_id]

    def remove_hyperedge(self, edge_id: int) -> None:
        """Remove hyperedge by ID."""
        if edge_id not in self._hyperedges:
            msg = f"Hyperedge {edge_id} not found"
            raise KeyError(msg)

        hyperedge = self._hyperedges[edge_id]

        # Update incidence
        for vid in hyperedge.vertices:
            self._incidence[vid].discard(edge_id)

        # Remove hyperedge
        del self._hyperedges[edge_id]

    def has_vertex(self, vertex_id: Any) -> bool:
        """Check if vertex exists."""
        return vertex_id in self._vertices

    def get_vertex(self, vertex_id: Any) -> Vertex:
        """Get vertex object."""
        if vertex_id not in self._vertices:
            msg = f"Vertex {vertex_id!r} not found"
            raise KeyError(msg)
        return self._vertices[vertex_id]

    def get_incident_hyperedges(self, vertex_id: Any) -> set[Hyperedge]:
        """Get all hyperedges incident to a vertex."""
        if vertex_id not in self._vertices:
            msg = f"Vertex {vertex_id!r} not found"
            raise KeyError(msg)

        return {self._hyperedges[eid] for eid in self._incidence[vertex_id]}

    def vertices(self) -> Iterator[Vertex]:
        """Iterate over vertices."""
        yield from self._vertices.values()

    def hyperedges(self) -> Iterator[Hyperedge]:
        """Iterate over hyperedges."""
        yield from self._hyperedges.values()

    def vertex_count(self) -> int:
        """Get vertex count."""
        return len(self._vertices)

    def hyperedge_count(self) -> int:
        """Get hyperedge count."""
        return len(self._hyperedges)

    def clear(self) -> None:
        """Clear all data."""
        self._vertices.clear()
        self._hyperedges.clear()
        self._incidence.clear()
        self._edge_counter = 0

    # Stub implementations for base class compatibility
    def add_edge(self, edge: Any) -> None:
        """Not applicable for hypergraphs - use add_hyperedge."""
        msg = "Use add_hyperedge() for hypergraphs, not add_edge()"
        raise NotImplementedError(msg)

    def remove_edge(self, source: Any, target: Any) -> None:
        """Not applicable for hypergraphs."""
        msg = "Use remove_hyperedge() for hypergraphs"
        raise NotImplementedError(msg)

    def has_edge(self, source: Any, target: Any) -> bool:
        """Not applicable for hypergraphs."""
        return False

    def get_neighbors(self, vertex_id: Any) -> set[Any]:
        """
        Get neighbors in hypergraph sense.

        Two vertices are neighbors if they share at least one hyperedge.
        """
        if vertex_id not in self._vertices:
            msg = f"Vertex {vertex_id!r} not found"
            raise KeyError(msg)

        neighbors = set()
        for edge_id in self._incidence[vertex_id]:
            hyperedge = self._hyperedges[edge_id]
            neighbors.update(hyperedge.vertices)

        neighbors.discard(vertex_id)  # Remove self
        return neighbors

    def get_edge(self, source: Any, target: Any) -> Any:
        """Not applicable for hypergraphs."""
        msg = "Hypergraphs don't have binary edges"
        raise NotImplementedError(msg)

    def edges(self) -> Iterator[Any]:
        """Return hyperedges (compatibility with base class)."""
        yield from self.hyperedges()

    def edge_count(self) -> int:
        """Get hyperedge count."""
        return self.hyperedge_count()


class Hypergraph(BaseGraph[Any, Any]):
    """
    Hypergraph: edges can connect any number of vertices.

    Unlike traditional graphs where edges connect exactly 2 vertices,
    hypergraphs allow edges to connect any subset of vertices.

    Examples:
        >>> hyper = Hypergraph()
        >>> hyper.add_vertex("A")
        >>> hyper.add_vertex("B")
        >>> hyper.add_vertex("C")
        >>> hyper.add_vertex("D")
        
        >>> # Regular edge (2 vertices)
        >>> hyper.add_hyperedge({"A", "B"}, weight=1.0)
        
        >>> # 3-way hyperedge
        >>> hyper.add_hyperedge({"B", "C", "D"}, weight=2.0)
        
        >>> # 4-way hyperedge
        >>> hyper.add_hyperedge({"A", "B", "C", "D"}, weight=3.0)
        
        >>> hyper.hyperedge_count()
        3
    """

    def __init__(self, **kwargs: Any) -> None:
        """
        Initialize hypergraph.

        Note: Hypergraphs are always undirected in this implementation.
        """
        super().__init__(directed=False, representation="hypergraph", **kwargs)

    def _create_representation(self, repr_type: str) -> GraphRepresentation:
        """Create hypergraph representation."""
        if repr_type != "hypergraph":
            msg = "Hypergraphs only support 'hypergraph' representation"
            raise ValueError(msg)
        return HypergraphRepresentation()

    def add_vertex(self, vertex_id: Any, **attributes: Any) -> None:
        """Add vertex to hypergraph."""
        vertex = Vertex(id=vertex_id, attributes=attributes)
        self._representation.add_vertex(vertex)
        self._notify_observers("vertex_added", vertex_id)

    def add_hyperedge(
        self,
        vertices: set[Any] | list[Any],
        *,
        weight: float = 1.0,
        **attributes: Any,
    ) -> None:
        """
        Add hyperedge connecting multiple vertices.

        Args:
            vertices: Set or list of vertex identifiers (≥2 vertices)
            weight: Hyperedge weight
            **attributes: Arbitrary metadata

        Raises:
            ValueError: If less than 2 vertices provided
            KeyError: If any vertex doesn't exist

        Examples:
            >>> hyper = Hypergraph()
            >>> hyper.add_vertex("A")
            >>> hyper.add_vertex("B")
            >>> hyper.add_vertex("C")
            >>> hyper.add_hyperedge({"A", "B", "C"}, weight=5.0)
        """
        vertex_set = set(vertices) if not isinstance(vertices, set) else vertices
        hyperedge = Hyperedge(vertex_set, weight=weight, **attributes)

        if not isinstance(self._representation, HypergraphRepresentation):
            msg = "Internal error: invalid representation type"
            raise TypeError(msg)

        self._representation.add_hyperedge(hyperedge)
        self._notify_observers("hyperedge_added", vertex_set)

    def add_edge(
        self,
        source: Any,
        target: Any,
        *,
        weight: float = 1.0,
        **attributes: Any,
    ) -> None:
        """
        Add binary edge (2-vertex hyperedge) for compatibility.

        This is a convenience method that creates a 2-vertex hyperedge.

        Args:
            source: First vertex
            target: Second vertex
            weight: Edge weight
            **attributes: Metadata
        """
        self.add_hyperedge({source, target}, weight=weight, **attributes)

    def remove_vertex(self, vertex_id: Any) -> None:
        """Remove vertex and all incident hyperedges."""
        self._representation.remove_vertex(vertex_id)
        self._notify_observers("vertex_removed", vertex_id)

    def remove_edge(self, source: Any, target: Any) -> None:
        """Not applicable for hypergraphs - use remove_hyperedge."""
        msg = "Use remove_hyperedge() for hypergraphs"
        raise NotImplementedError(msg)

    def has_vertex(self, vertex_id: Any) -> bool:
        """Check if vertex exists."""
        return self._representation.has_vertex(vertex_id)

    def has_edge(self, source: Any, target: Any) -> bool:
        """
        Check if 2-vertex hyperedge exists.

        Args:
            source: First vertex
            target: Second vertex

        Returns:
            True if hyperedge containing exactly these 2 vertices exists
        """
        if not isinstance(self._representation, HypergraphRepresentation):
            return False

        for hyperedge in self._representation.hyperedges():
            if hyperedge.vertices == {source, target}:
                return True
        return False

    def get_neighbors(self, vertex_id: Any) -> set[Any]:
        """
        Get neighbors (vertices sharing hyperedges).

        Args:
            vertex_id: Vertex to get neighbors for

        Returns:
            Set of vertices that share at least one hyperedge with vertex_id
        """
        return self._representation.get_neighbors(vertex_id)

    def vertices(self) -> Iterator[Vertex]:
        """Iterate over vertices."""
        yield from self._representation.vertices()

    def edges(self) -> Iterator[Hyperedge]:
        """Iterate over hyperedges."""
        if isinstance(self._representation, HypergraphRepresentation):
            yield from self._representation.hyperedges()

    def get_incident_hyperedges(self, vertex_id: Any) -> set[Hyperedge]:
        """
        Get all hyperedges incident to a vertex.

        Args:
            vertex_id: Vertex identifier

        Returns:
            Set of Hyperedge objects containing this vertex

        Examples:
            >>> hyper = Hypergraph()
            >>> hyper.add_vertex("A")
            >>> hyper.add_vertex("B")
            >>> hyper.add_vertex("C")
            >>> hyper.add_hyperedge({"A", "B"})
            >>> hyper.add_hyperedge({"A", "C"})
            >>> len(hyper.get_incident_hyperedges("A"))
            2
        """
        if not isinstance(self._representation, HypergraphRepresentation):
            return set()
        return self._representation.get_incident_hyperedges(vertex_id)

    def get_hyperedges_containing(self, vertex_id: Any) -> set[Hyperedge]:
        """
        Get all hyperedges containing a vertex.
        Alias for get_incident_hyperedges.
        """
        return self.get_incident_hyperedges(vertex_id)

    def hyperedge_count(self) -> int:
        """Get total number of hyperedges."""
        if isinstance(self._representation, HypergraphRepresentation):
            return self._representation.hyperedge_count()
        return 0

    def degree(self, vertex_id: Any) -> int:
        """
        Get degree of vertex (number of incident hyperedges).

        Args:
            vertex_id: Vertex identifier

        Returns:
            Number of hyperedges incident to this vertex
        """
        return len(self.get_incident_hyperedges(vertex_id))

    def to_bipartite_graph(self) -> SimpleGraph:
        """
        Convert hypergraph to bipartite graph representation.

        Creates a bipartite graph with:
        - One set of nodes for vertices
        - One set of nodes for hyperedges
        - Edges connecting vertices to their incident hyperedges

        Returns:
            SimpleGraph representing the bipartite structure

        Examples:
            >>> hyper = Hypergraph()
            >>> hyper.add_vertex("A")
            >>> hyper.add_vertex("B")
            >>> hyper.add_vertex("C")
            >>> hyper.add_hyperedge({"A", "B", "C"}, weight=5.0)
            >>> bipartite = hyper.to_bipartite_graph()
        """
        from packages.graphs.simple_graph import SimpleGraph

        bipartite = SimpleGraph(directed=False)

        # Add vertex nodes
        for vertex in self.vertices():
            bipartite.add_vertex(f"v_{vertex.id}", **vertex.attributes)

        # Add hyperedge nodes and connect them
        for i, hyperedge in enumerate(self.edges()):
            edge_id = f"e_{i}"
            bipartite.add_vertex(edge_id, type="hyperedge", weight=hyperedge.weight)

            # Connect to all incident vertices
            for vid in hyperedge.vertices:
                bipartite.add_edge(f"v_{vid}", edge_id, weight=hyperedge.weight)

        return bipartite
