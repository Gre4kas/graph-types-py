"""
Format converters for exporting/importing to standard Python structures.

This module handles conversions between Graph objects and Python native
types like Dictionaries (adjacency dicts) or Lists (edge lists).
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, List, Tuple

if TYPE_CHECKING:
    from packages.core.base_graph import BaseGraph
    from packages.graphs.simple_graph import SimpleGraph


def to_adjacency_dict(graph: BaseGraph) -> Dict[Any, Dict[Any, float]]:
    """
    Convert graph to a standard Python dictionary of dictionaries.

    Format: {source_id: {target_id: weight, ...}, ...}

    Args:
        graph: The source graph.

    Returns:
        Dictionary representing the adjacency structure.

    Note:
        This conversion loses vertex/edge attributes (except weight).
        It is primarily used for structure export.

    Examples:
        >>> graph = SimpleGraph()
        >>> graph.add_edge("A", "B", weight=5.0)
        >>> data = to_adjacency_dict(graph)
        >>> data["A"]["B"]
        5.0
    """
    adj_dict: Dict[Any, Dict[Any, float]] = {}

    # Initialize dict for all vertices to ensure isolated vertices are included
    for vertex in graph.vertices():
        adj_dict[vertex.id] = {}

    # Fill edges
    for edge in graph.edges():
        if edge.source not in adj_dict:
            adj_dict[edge.source] = {}
        
        # For multigraphs, this might overwrite previous edges with the last one found.
        # This function assumes simple structure logic.
        adj_dict[edge.source][edge.target] = edge.weight

        # If undirected, ensure symmetry
        if not graph.is_directed():
            if edge.target not in adj_dict:
                adj_dict[edge.target] = {}
            adj_dict[edge.target][edge.source] = edge.weight

    return adj_dict


def from_adjacency_dict(
    data: Dict[Any, Dict[Any, float]],
    directed: bool = False,
) -> SimpleGraph:
    """
    Create a SimpleGraph from a standard adjacency dictionary.

    Args:
        data: Dictionary {source: {target: weight}}.
        directed: Whether the resulting graph should be directed.

    Returns:
        A new SimpleGraph instance.

    Examples:
        >>> data = {"A": {"B": 2.5}, "B": {}}
        >>> graph = from_adjacency_dict(data, directed=True)
        >>> graph.get_edge("A", "B").weight
        2.5
    """
    from packages.graphs.simple_graph import SimpleGraph

    graph = SimpleGraph(directed=directed)

    # 1. Add all vertices first
    for source_id in data:
        if not graph.has_vertex(source_id):
            graph.add_vertex(source_id)
        
        for target_id in data[source_id]:
            if not graph.has_vertex(target_id):
                graph.add_vertex(target_id)

    # 2. Add edges
    for source_id, neighbors in data.items():
        for target_id, weight in neighbors.items():
            # For undirected graphs, avoid adding the edge twice
            if not directed and graph.has_edge(target_id, source_id):
                continue
            
            if not graph.has_edge(source_id, target_id):
                graph.add_edge(source_id, target_id, weight=weight)

    return graph


def to_edge_list_tuples(graph: BaseGraph) -> List[Tuple[Any, Any, float]]:
    """
    Convert graph to a list of (source, target, weight) tuples.

    Args:
        graph: The source graph.

    Returns:
        List of tuples.

    Examples:
        >>> graph = SimpleGraph()
        >>> graph.add_edge("A", "B", weight=3.0)
        >>> to_edge_list_tuples(graph)
        [('A', 'B', 3.0)]
    """
    result = []
    for edge in graph.edges():
        result.append((edge.source, edge.target, edge.weight))
    return result