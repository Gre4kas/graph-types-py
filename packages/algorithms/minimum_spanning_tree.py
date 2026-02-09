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


def prim_mst(graph: BaseGraph[Any, Any]) -> BaseGraph[Any, Any]:
    """
    Prim's algorithm for Minimum Spanning Tree.

    Time Complexity: O(E log V) ignoring priority queue operations on dense graphs.
    
    Args:
        graph: Undirected weighted graph
    
    Returns:
        A new graph containing only the MST edges
    
    Raises:
        ValueError: If graph is directed
    """
    if graph.is_directed():
        msg = "MST only defined for undirected graphs"
        raise ValueError(msg)

    # Initialize MST graph (same type as original)
    from packages.graphs.simple_graph import SimpleGraph
    mst = SimpleGraph(directed=False)
    
    if graph.vertex_count() == 0:
        return mst

    # Start from arbitrary vertex
    start_node = next(graph.vertices()).id
    mst.add_vertex(start_node)
    
    visited = {start_node}
    edges = []
    
    # Add initial edges to heap
    for neighbor in graph.get_neighbors(start_node):
        edge = graph.get_edge(start_node, neighbor)
        heapq.heappush(edges, (edge.weight, edge))
        
    while edges:
        weight, edge = heapq.heappop(edges)
        
        # Determine which stored vertex is new
        if edge.source in visited and edge.target in visited:
            continue
            
        if edge.source in visited:
            new_vertex = edge.target
        else:
            new_vertex = edge.source
            
        # Add to MST
        if not mst.has_vertex(new_vertex):
            mst.add_vertex(new_vertex)
        mst.add_edge(edge.source, edge.target, weight=weight)
        visited.add(new_vertex)
        
        # Add new edges
        for neighbor in graph.get_neighbors(new_vertex):
            if neighbor not in visited:
                next_edge = graph.get_edge(new_vertex, neighbor)
                heapq.heappush(edges, (next_edge.weight, next_edge))
                
    return mst
