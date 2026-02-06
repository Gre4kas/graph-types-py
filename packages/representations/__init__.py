"""Graph representation strategies.

This module provides different storage strategies for graph structures,
following the Strategy pattern for clean polymorphism and separation of concerns.

Available Representations:
    - GraphRepresentation: Abstract base class defining the unified contract
    - SimpleAdjacencyListRepresentation: Fast set-based storage for simple graphs
    - MultiAdjacencyListRepresentation: List-based storage for multigraphs
    - HypergraphRepresentation: Incidence list storage for hypergraphs

Design Principles:
    - Strategy Pattern: Interchangeable storage implementations
    - SOLID: Single responsibility per class, open for extension
    - Performance: Optimized hot paths (has_edge, get_neighbors)
    - Type Safety: Full type hints with Pydantic validation

Examples:
    >>> from packages.representations import SimpleAdjacencyListRepresentation
    >>> from packages.core import Vertex, Edge
    >>> 
    >>> repr = SimpleAdjacencyListRepresentation()
    >>> repr.add_vertex(Vertex(id="A"))
    >>> repr.add_vertex(Vertex(id="B"))
    >>> repr.add_edge(Edge(source="A", target="B", weight=5.0))
    >>> repr.has_edge("A", "B")
    True
"""

from packages.representations.adjacency_list_multi import (
    MultiAdjacencyListRepresentation,
)
from packages.representations.adjacency_list_simple import (
    SimpleAdjacencyListRepresentation,
)
from packages.representations.base_representation import GraphRepresentation
from packages.representations.hypergraph_representation import (
    HypergraphRepresentation,
)

__all__ = [
    "GraphRepresentation",
    "SimpleAdjacencyListRepresentation",
    "MultiAdjacencyListRepresentation",
    "HypergraphRepresentation",
]
