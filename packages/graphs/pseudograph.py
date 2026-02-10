"""
Pseudograph implementation (multiple edges + self-loops allowed).

Mathematical definition: Most general simple structure allowing both
self-loops and multiple edges between vertices.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from packages.graphs.multigraph import Multigraph, MultigraphRepresentation
from packages.core.edge import Edge
from packages.core.vertex import Vertex
from packages.representations.base_representation import GraphRepresentation

if TYPE_CHECKING:
    from collections.abc import Iterator


class Pseudograph(Multigraph):
    """
    Pseudograph: allows both multiple edges AND self-loops.

    This is the most permissive graph type in classical graph theory,
    placing no restrictions on edge structure.

    Examples:
        >>> pseudo = Pseudograph()
        >>> pseudo.add_vertex("A")
        >>> pseudo.add_vertex("B")
        
        >>> # Self-loops allowed
        >>> pseudo.add_edge("A", "A", weight=1.0)
        
        >>> # Multiple edges allowed
        >>> pseudo.add_edge("A", "B", weight=3.0)
        >>> pseudo.add_edge("A", "B", weight=5.0)
        
        >>> pseudo.edge_count()
        3
        
        >>> # Check for self-loops
        >>> pseudo.has_self_loop("A")
        True
    """

    def add_edge(
        self,
        source: Any,
        target: Any,
        *,
        weight: float = 1.0,
        **attributes: Any,
    ) -> None:
        """
        Add edge to pseudograph.

        Unlike simple graphs and multigraphs, self-loops ARE allowed.
        Multiple edges between same vertices ARE allowed.

        Args:
            source: Source vertex identifier
            target: Target vertex identifier
            weight: Edge weight (default: 1.0)
            **attributes: Arbitrary edge metadata

        Raises:
            VertexNotFoundError: If source or target doesn't exist

        Examples:
            >>> pseudo = Pseudograph()
            >>> pseudo.add_vertex("A")
            >>> pseudo.add_edge("A", "A", weight=2.0)  # Self-loop OK
            >>> pseudo.add_edge("A", "A", weight=3.0)  # Multiple self-loops OK
        """
        # No constraint checks - everything is allowed in pseudograph
        edge = Edge(
            source=source,
            target=target,
            weight=weight,
            directed=self._directed,
            attributes=attributes,
        )
        self._representation.add_edge(edge)
        self._notify_observers("edge_added", source, target)

    def has_self_loop(self, vertex_id: Any) -> bool:
        """
        Check if vertex has any self-loops.

        Args:
            vertex_id: Vertex to check

        Returns:
            True if vertex has at least one self-loop

        Examples:
            >>> pseudo = Pseudograph()
            >>> pseudo.add_vertex("A")
            >>> pseudo.has_self_loop("A")
            False
            >>> pseudo.add_edge("A", "A")
            >>> pseudo.has_self_loop("A")
            True
        """
        for edge in self.edges():
            if edge.source == vertex_id and edge.target == vertex_id:
                return True
        return False

    def self_loop_count(self, vertex_id: Any) -> int:
        """
        Count number of self-loops on a vertex.

        Args:
            vertex_id: Vertex to count self-loops for

        Returns:
            Number of self-loops

        Examples:
            >>> pseudo = Pseudograph()
            >>> pseudo.add_vertex("A")
            >>> pseudo.add_edge("A", "A", weight=1.0)
            >>> pseudo.add_edge("A", "A", weight=2.0)
            >>> pseudo.self_loop_count("A")
            2
        """
        count = 0
        for edge in self.edges():
            if edge.source == vertex_id and edge.target == vertex_id:
                count += 1
        return count

    def count_self_loops(self) -> int:
        """Count total number of self-loops in the graph."""
        count = 0
        for edge in self.edges():
            if edge.source == edge.target:
                count += 1
        return count

    def total_degree(self, vertex_id: Any) -> int:
        """
        Get total degree of vertex (self-loops count twice).

        In graph theory, each self-loop contributes 2 to the degree.

        Args:
            vertex_id: Vertex to calculate degree for

        Returns:
            Total degree (neighbors + 2×self-loops)

        Examples:
            >>> pseudo = Pseudograph()
            >>> pseudo.add_vertex("A")
            >>> pseudo.add_vertex("B")
            >>> pseudo.add_edge("A", "B")
            >>> pseudo.add_edge("A", "A")  # Self-loop
            >>> pseudo.total_degree("A")  # 1 (neighbor B) + 2 (self-loop) = 3
            3
        """
        degree = len(self.get_neighbors(vertex_id))
        self_loops = self.self_loop_count(vertex_id)
        return degree + (2 * self_loops)

    def remove_all_self_loops(self) -> int:
        """
        Remove all self-loops from the graph.

        Returns:
            Number of self-loops removed

        Examples:
            >>> pseudo = Pseudograph()
            >>> pseudo.add_vertex("A")
            >>> pseudo.add_edge("A", "A")
            >>> pseudo.add_edge("A", "A")
            >>> removed = pseudo.remove_all_self_loops()
            >>> removed
            2
            >>> pseudo.has_self_loop("A")
            False
        """
        removed_count = 0
        
        # Collect self-loops to remove
        self_loops = []
        for edge in self.edges():
            if edge.is_self_loop():
                self_loops.append((edge.source, edge.target))
        
        # Remove them
        for source, target in self_loops:
            try:
                self.remove_edge(source, target)
                removed_count += 1
            except KeyError:
                pass  # Already removed
        
        return removed_count


def example_pseudograph_usage() -> None:
    """Demonstrate pseudograph-specific features."""
    print("=" * 60)
    print("PSEUDOGRAPH EXAMPLE")
    print("=" * 60)

    pseudo = Pseudograph()
    
    # Add vertices
    pseudo.add_vertex("A")
    pseudo.add_vertex("B")
    pseudo.add_vertex("C")
    
    # Add various edge types
    pseudo.add_edge("A", "B", weight=5.0, label="regular")
    pseudo.add_edge("A", "B", weight=3.0, label="parallel")  # Parallel edge
    pseudo.add_edge("A", "A", weight=2.0, label="self-loop1")  # Self-loop
    pseudo.add_edge("A", "A", weight=1.0, label="self-loop2")  # Another self-loop
    pseudo.add_edge("B", "C", weight=4.0, label="regular")
    
    print(f"\nPseudograph: {pseudo}")
    print(f"Total edges: {pseudo.edge_count()}")
    
    print("\nAll edges:")
    for edge in pseudo.edges():
        loop_indicator = " (SELF-LOOP)" if edge.is_self_loop() else ""
        print(f"  {edge}{loop_indicator}")
    
    print(f"\nVertex A has self-loop: {pseudo.has_self_loop('A')}")
    print(f"Self-loop count on A: {pseudo.self_loop_count('A')}")
    print(f"Regular degree of A: {pseudo.degree('A')}")
    print(f"Total degree of A: {pseudo.total_degree('A')}")
    
    print(f"\nRemoving all self-loops...")
    removed = pseudo.remove_all_self_loops()
    print(f"Removed {removed} self-loops")
    print(f"Remaining edges: {pseudo.edge_count()}")
    
    print()
