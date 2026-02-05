"""
Adapter for NetworkX compatibility.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from packages.core.base_graph import BaseGraph

try:
    import networkx as nx
    NETWORKX_AVAILABLE = True
except ImportError:
    NETWORKX_AVAILABLE = False


def to_networkx(graph: BaseGraph[Any, Any]) -> Any:
    """
    Convert graph to NetworkX format.

    Args:
        graph: Source graph

    Returns:
        NetworkX Graph or DiGraph

    Raises:
        ImportError: If NetworkX not installed

    Examples:
        >>> graph = SimpleGraph()
        >>> graph.add_edge("A", "B", weight=5.0)
        >>> nx_graph = to_networkx(graph)
        >>> nx.shortest_path(nx_graph, "A", "B")
        ['A', 'B']
    """
    if not NETWORKX_AVAILABLE:
        msg = "NetworkX not installed. Install with: pip install networkx"
        raise ImportError(msg)

    # Create appropriate NetworkX graph type
    if graph.is_directed():
        nx_graph = nx.DiGraph()
    else:
        nx_graph = nx.Graph()

    # Add vertices with attributes
    for vertex in graph.vertices():
        nx_graph.add_node(vertex.id, **vertex.attributes)

    # Add edges with attributes
    for edge in graph.edges():
        nx_graph.add_edge(
            edge.source,
            edge.target,
            weight=edge.weight,
            **edge.attributes,
        )

    return nx_graph


def from_networkx(nx_graph: Any, graph_type: str = "simple") -> BaseGraph[Any, Any]:
    """
    Convert NetworkX graph to our format.

    Args:
        nx_graph: NetworkX Graph or DiGraph
        graph_type: Type of graph to create ("simple", "multi", "pseudo")

    Returns:
        Graph instance

    Examples:
        >>> nx_graph = nx.karate_club_graph()
        >>> graph = from_networkx(nx_graph)
    """
    if not NETWORKX_AVAILABLE:
        msg = "NetworkX not installed"
        raise ImportError(msg)

    from packages.graphs.simple_graph import SimpleGraph
    from packages.graphs.multigraph import Multigraph
    from packages.graphs.pseudograph import Pseudograph

    # Create appropriate graph type
    directed = nx_graph.is_directed()
    
    if graph_type == "simple":
        graph = SimpleGraph(directed=directed)
    elif graph_type == "multi":
        graph = Multigraph(directed=directed)
    elif graph_type == "pseudo":
        graph = Pseudograph(directed=directed)
    else:
        msg = f"Unknown graph type: {graph_type}"
        raise ValueError(msg)

    # Add vertices
    for node, attrs in nx_graph.nodes(data=True):
        graph.add_vertex(node, **attrs)

    # Add edges
    for u, v, attrs in nx_graph.edges(data=True):
        weight = attrs.pop("weight", 1.0)
        graph.add_edge(u, v, weight=weight, **attrs)

    return graph
