"""
Representation converters for changing graph storage strategies.

This module provides utilities to switch the underlying data structure
of a graph (e.g., from Adjacency List to Adjacency Matrix) while
preserving the graph's topology and attributes.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from packages.core.base_graph import BaseGraph


class RepresentationConverter:
    """
    Static utility for converting graph representations.
    """

    @staticmethod
    def convert(
        graph: BaseGraph,
        target_representation: str,
    ) -> BaseGraph:
        """
        Convert a graph to use a different internal representation.

        Creates a new graph instance of the same type (Simple, Multi, etc.)
        but with the specified storage strategy.

        Args:
            graph: The source graph instance.
            target_representation: The target representation type.
                Options: "adjacency_list", "adjacency_matrix", "edge_list".

        Returns:
            A new graph instance with the requested representation.

        Raises:
            ValueError: If the target representation is unknown.

        Examples:
            >>> graph = SimpleGraph(representation="adjacency_list")
            >>> graph.add_edge("A", "B")
            >>> matrix_graph = RepresentationConverter.convert(graph, "adjacency_matrix")
            >>> matrix_graph.has_edge("A", "B")
            True
        """
        # Create a new instance of the same graph class (SimpleGraph, Multigraph, etc.)
        # We pass the new representation string to the constructor.
        new_graph = graph.__class__(
            directed=graph.is_directed(),
            representation=target_representation,
        )

        # 1. Copy Vertices and their attributes
        for vertex in graph.vertices():
            new_graph.add_vertex(vertex.id, **vertex.attributes)

        # 2. Copy Edges and their attributes
        for edge in graph.edges():
            # Check for duplicates if converting to a representation that might
            # handle them differently, though the Graph class logic usually handles this.
            new_graph.add_edge(
                edge.source,
                edge.target,
                weight=edge.weight,
                **edge.attributes,
            )

        return new_graph