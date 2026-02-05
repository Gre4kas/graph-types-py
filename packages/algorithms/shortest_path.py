"""
Shortest path algorithms for weighted graphs.

This module implements Dijkstra's algorithm with heap optimization
and Bellman-Ford for negative weights.
"""

from __future__ import annotations

import heapq
import math
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from packages.core.base_graph import BaseGraph


def dijkstra(
    graph: BaseGraph[Any, Any],
    source: Any,
    target: Any | None = None,
) -> dict[Any, float] | tuple[dict[Any, float], dict[Any, Any]]:
    """
    Dijkstra's shortest path algorithm with heap optimization.

    Time Complexity: O((|V| + |E|) log |V|) with binary heap
    Space Complexity: O(|V|)

    Args:
        graph: Weighted graph (non-negative weights)
        source: Source vertex identifier
        target: Optional target vertex (if None, computes to all vertices)

    Returns:
        If target is None: dict mapping vertex -> distance from source
        If target is provided: (distances, predecessors) for path reconstruction

    Raises:
        KeyError: If source or target vertex doesn't exist
        ValueError: If graph contains negative weights

    Examples:
        >>> graph = SimpleGraph()
        >>> graph.add_edge("A", "B", weight=4.0)
        >>> graph.add_edge("B", "C", weight=3.0)
        >>> graph.add_edge("A", "C", weight=10.0)
        >>> distances = dijkstra(graph, "A")
        >>> distances["C"]
        7.0

        >>> distances, predecessors = dijkstra(graph, "A", "C")
        >>> reconstruct_path(predecessors, "A", "C")
        ['A', 'B', 'C']
    """
    if not graph.has_vertex(source):
        msg = f"Source vertex {source!r} not found"
        raise KeyError(msg)

    if target is not None and not graph.has_vertex(target):
        msg = f"Target vertex {target!r} not found"
        raise KeyError(msg)

    # Initialize distances
    distances: dict[Any, float] = {vertex.id: math.inf for vertex in graph.vertices()}
    distances[source] = 0.0

    # Track predecessors for path reconstruction
    predecessors: dict[Any, Any | None] = {vertex.id: None for vertex in graph.vertices()}

    # Priority queue: (distance, vertex)
    heap: list[tuple[float, Any]] = [(0.0, source)]
    visited: set[Any] = set()

    while heap:
        current_dist, current = heapq.heappop(heap)

        # Skip if already processed
        if current in visited:
            continue

        visited.add(current)

        # Early termination if target reached
        if target is not None and current == target:
            break

        # Relax edges
        for neighbor in graph.get_neighbors(current):
            if neighbor in visited:
                continue

            # Get edge weight
            edge = graph._representation.get_edge(current, neighbor)
            weight = edge.weight

            if weight < 0:
                msg = "Dijkstra's algorithm requires non-negative weights"
                raise ValueError(msg)

            new_dist = current_dist + weight

            if new_dist < distances[neighbor]:
                distances[neighbor] = new_dist
                predecessors[neighbor] = current
                heapq.heappush(heap, (new_dist, neighbor))

    if target is not None:
        return distances, predecessors

    return distances


def reconstruct_path(
    predecessors: dict[Any, Any | None],
    source: Any,
    target: Any,
) -> list[Any] | None:
    """
    Reconstruct shortest path from predecessors dictionary.

    Args:
        predecessors: Dictionary from Dijkstra/Bellman-Ford
        source: Source vertex identifier
        target: Target vertex identifier

    Returns:
        List of vertex IDs in path from source to target, or None if no path

    Examples:
        >>> predecessors = {'A': None, 'B': 'A', 'C': 'B'}
        >>> reconstruct_path(predecessors, 'A', 'C')
        ['A', 'B', 'C']
    """
    if predecessors[target] is None and target != source:
        return None  # No path exists

    path: list[Any] = []
    current = target

    while current is not None:
        path.append(current)
        current = predecessors[current]

    path.reverse()
    return path


def bellman_ford(
    graph: BaseGraph[Any, Any],
    source: Any,
) -> dict[Any, float] | None:
    """
    Bellman-Ford shortest path algorithm (handles negative weights).

    Time Complexity: O(|V| × |E|)
    Space Complexity: O(|V|)

    Args:
        graph: Weighted graph (may have negative weights)
        source: Source vertex identifier

    Returns:
        Dictionary mapping vertex -> distance from source,
        or None if negative cycle detected

    Raises:
        KeyError: If source vertex doesn't exist

    Examples:
        >>> graph = SimpleGraph(directed=True)
        >>> graph.add_edge("A", "B", weight=-1.0)
        >>> graph.add_edge("B", "C", weight=3.0)
        >>> distances = bellman_ford(graph, "A")
        >>> distances["C"]
        2.0
    """
    if not graph.has_vertex(source):
        msg = f"Source vertex {source!r} not found"
        raise KeyError(msg)

    # Initialize distances
    distances: dict[Any, float] = {vertex.id: math.inf for vertex in graph.vertices()}
    distances[source] = 0.0

    # Relax edges |V| - 1 times
    vertex_count = graph.vertex_count()
    for _ in range(vertex_count - 1):
        for edge in graph.edges():
            src, tgt = edge.source, edge.target
            weight = edge.weight

            if distances[src] != math.inf:
                new_dist = distances[src] + weight
                if new_dist < distances[tgt]:
                    distances[tgt] = new_dist

    # Check for negative cycles
    for edge in graph.edges():
        src, tgt = edge.source, edge.target
        weight = edge.weight

        if distances[src] != math.inf:
            if distances[src] + weight < distances[tgt]:
                return None  # Negative cycle detected

    return distances


def floyd_warshall(graph: BaseGraph[Any, Any]) -> dict[tuple[Any, Any], float]:
    """
    Floyd-Warshall all-pairs shortest paths algorithm.

    Time Complexity: O(|V|³)
    Space Complexity: O(|V|²)

    Args:
        graph: Weighted graph

    Returns:
        Dictionary mapping (source, target) -> shortest distance

    Examples:
        >>> graph = SimpleGraph()
        >>> graph.add_edge("A", "B", weight=2.0)
        >>> graph.add_edge("B", "C", weight=3.0)
        >>> distances = floyd_warshall(graph)
        >>> distances[("A", "C")]
        5.0
    """
    vertices = [v.id for v in graph.vertices()]
    n = len(vertices)

    # Initialize distance matrix
    dist: dict[tuple[Any, Any], float] = {}

    # Set initial distances
    for i, u in enumerate(vertices):
        for j, v in enumerate(vertices):
            if i == j:
                dist[(u, v)] = 0.0
            else:
                dist[(u, v)] = math.inf

    # Add edge weights
    for edge in graph.edges():
        dist[(edge.source, edge.target)] = edge.weight

    # Floyd-Warshall algorithm
    for k in vertices:
        for i in vertices:
            for j in vertices:
                if dist[(i, k)] + dist[(k, j)] < dist[(i, j)]:
                    dist[(i, j)] = dist[(i, k)] + dist[(k, j)]

    return dist
