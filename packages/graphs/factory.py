"""
Graph Factory for creating graph instances.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from packages.core.base_graph import BaseGraph

class GraphFactory:
    """
    Factory for creating graph instances based on type and configuration.
    """

    @staticmethod
    def create_graph(
        graph_type: str,
        directed: bool = False,
        representation: str = "adjacency_list",
        **kwargs: Any,
    ) -> BaseGraph:
        """
        Create a graph instance.

        Args:
            graph_type: Type of graph ("simple", "multi", "pseudo", "hyper")
            directed: Whether the graph is directed
            representation: Internal representation strategy
            **kwargs: Additional arguments passed to graph constructor

        Returns:
            A new graph instance

        Raises:
            ValueError: If graph_type is unknown
        """
        from packages.graphs.simple_graph import SimpleGraph
        from packages.graphs.multigraph import Multigraph
        from packages.graphs.pseudograph import Pseudograph
        from packages.graphs.hypergraph import Hypergraph

        graph_type = graph_type.lower()

        if graph_type == "simple":
            return SimpleGraph(directed=directed, representation=representation, **kwargs)
        elif graph_type == "multi":
            return Multigraph(directed=directed, representation=representation, **kwargs)
        elif graph_type == "pseudo":
            return Pseudograph(directed=directed, representation=representation, **kwargs)
        elif graph_type == "hyper":
            # Hypergraphs might have different constructor signatures or limited representation support
            # For now, we assume basic compatibility or ignore specific kwargs if needed
            return Hypergraph(representation=representation, **kwargs)
        else:
            raise ValueError(f"Unknown graph type: {graph_type}")