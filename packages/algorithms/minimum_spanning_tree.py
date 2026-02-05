"""
Minimum Spanning Tree algorithms.
"""

from __future__ import annotations

import heapq
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from packages.core.base_graph import BaseGraph
    from packages.core.edge import Edge


def kruskal_mst(graph: BaseGraph[Any, Any]) -> list[Edge]:
    """
    Kruskal's algorithm for Minimum Spanning Tree.

    Time Complexity: O(E log E)
    
    Args:
        graph: Undirected weighted graph
    
    Returns:
        List of edges in MST
    
    Examples:
        >>> graph = SimpleGraph()
        >>> graph.add_edge("A", "B", weight=4.0)
        >>> graph.add_edge("B", "C", weight=8.0)
        >>> graph.add_edge("A", "C", weight=7.0)
        >>> mst = kruskal_mst(graph)
        >>> sum(e.weight for e in mst)
        11.0
    """
    if graph.is_directed():
        msg = "MST only defined for undirected graphs"
        raise ValueError(msg)

    # Sort edges by weight
    sorted_edges = sorted(graph.edges(), key=lambda e: e.weight)
    
    # Union-Find data structure
    parent: dict[Any, Any] = {v.id: v.id for v in graph.vertices()}
    
    def find(x: Any) -> Any:
        if parent[x] != x:
            parent[x] = find(parent[x])
        return parent[x]
    
    def union(x: Any, y: Any) -> None:
        px, py = find(x), find(y)
        parent[px] = py
    
    # Kruskal's algorithm
    mst: list[Edge] = []
    for edge in sorted_edges:
        if find(edge.source) != find(edge.target):
            mst.append(edge)
            union(edge.source, edge.target)
    
    return mst
