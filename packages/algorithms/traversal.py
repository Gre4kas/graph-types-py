"""
Graph traversal algorithms: BFS, DFS.

This module implements breadth-first search and depth-first search
with both iterative and recursive approaches, following the Template Method pattern.
"""

from __future__ import annotations

from collections import deque
from collections.abc import Iterator
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from packages.core.base_graph import BaseGraph


def bfs(
    graph: BaseGraph[Any, Any],
    start: Any,
    *,
    yield_depth: bool = False,
) -> Iterator[Any] | Iterator[tuple[Any, int]]:
    """
    Breadth-First Search traversal.

    Time Complexity: O(|V| + |E|)
    Space Complexity: O(|V|)

    Args:
        graph: Graph to traverse
        start: Starting vertex identifier
        yield_depth: If True, yield (vertex, depth) tuples

    Yields:
        Vertex identifiers in BFS order, optionally with depth

    Raises:
        KeyError: If start vertex doesn't exist

    Examples:
        >>> graph = SimpleGraph()
        >>> graph.add_vertex("A")
        >>> graph.add_vertex("B")
        >>> graph.add_vertex("C")
        >>> graph.add_edge("A", "B")
        >>> graph.add_edge("B", "C")
        >>> list(bfs(graph, "A"))
        ['A', 'B', 'C']

        >>> list(bfs(graph, "A", yield_depth=True))
        [('A', 0), ('B', 1), ('C', 2)]
    """
    if not graph.has_vertex(start):
        msg = f"Start vertex {start!r} not found"
        raise KeyError(msg)

    visited: set[Any] = set()
    queue: deque[tuple[Any, int]] = deque([(start, 0)])
    visited.add(start)

    while queue:
        vertex, depth = queue.popleft()

        if yield_depth:
            yield vertex, depth
        else:
            yield vertex

        # Enqueue unvisited neighbors
        for neighbor in graph.get_neighbors(vertex):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, depth + 1))


def dfs(
    graph: BaseGraph[Any, Any],
    start: Any,
    *,
    recursive: bool = False,
) -> Iterator[Any]:
    """
    Depth-First Search traversal.

    Time Complexity: O(|V| + |E|)
    Space Complexity: O(|V|)

    Args:
        graph: Graph to traverse
        start: Starting vertex identifier
        recursive: Use recursive implementation (default: False, iterative)

    Yields:
        Vertex identifiers in DFS order

    Raises:
        KeyError: If start vertex doesn't exist

    Examples:
        >>> graph = SimpleGraph()
        >>> graph.add_edge("A", "B")
        >>> graph.add_edge("B", "C")
        >>> list(dfs(graph, "A"))
        ['A', 'B', 'C']

        >>> list(dfs(graph, "A", recursive=True))
        ['A', 'B', 'C']
    """
    if not graph.has_vertex(start):
        msg = f"Start vertex {start!r} not found"
        raise KeyError(msg)

    if recursive:
        yield from _dfs_recursive(graph, start, set())
    else:
        yield from _dfs_iterative(graph, start)


def _dfs_iterative(graph: BaseGraph[Any, Any], start: Any) -> Iterator[Any]:
    """
    Iterative DFS implementation using explicit stack.

    Args:
        graph: Graph to traverse
        start: Starting vertex identifier

    Yields:
        Vertex identifiers in DFS order
    """
    visited: set[Any] = set()
    stack: list[Any] = [start]

    while stack:
        vertex = stack.pop()

        if vertex in visited:
            continue

        visited.add(vertex)
        yield vertex

        # Push unvisited neighbors (reverse order for left-to-right traversal)
        neighbors = sorted(graph.get_neighbors(vertex), reverse=True)
        for neighbor in neighbors:
            if neighbor not in visited:
                stack.append(neighbor)


def _dfs_recursive(
    graph: BaseGraph[Any, Any],
    vertex: Any,
    visited: set[Any],
) -> Iterator[Any]:
    """
    Recursive DFS implementation.

    Args:
        graph: Graph to traverse
        vertex: Current vertex identifier
        visited: Set of visited vertices

    Yields:
        Vertex identifiers in DFS order
    """
    visited.add(vertex)
    yield vertex

    for neighbor in sorted(graph.get_neighbors(vertex)):
        if neighbor not in visited:
            yield from _dfs_recursive(graph, neighbor, visited)


def connected_components(graph: BaseGraph[Any, Any]) -> list[set[Any]]:
    """
    Find all connected components in an undirected graph.

    Time Complexity: O(|V| + |E|)

    Args:
        graph: Undirected graph

    Returns:
        List of sets, each containing vertex IDs of a connected component

    Raises:
        ValueError: If graph is directed

    Examples:
        >>> graph = SimpleGraph()
        >>> graph.add_edge("A", "B")
        >>> graph.add_edge("C", "D")
        >>> components = connected_components(graph)
        >>> len(components)
        2
        >>> {'A', 'B'} in components
        True
    """
    if graph.is_directed():
        msg = "Connected components only defined for undirected graphs"
        raise ValueError(msg)

    visited: set[Any] = set()
    components: list[set[Any]] = []

    for vertex in graph.vertices():
        vertex_id = vertex.id
        if vertex_id not in visited:
            # BFS to find component
            component = set(bfs(graph, vertex_id))
            components.append(component)
            visited.update(component)

    return components


def is_connected(graph: BaseGraph[Any, Any]) -> bool:
    """
    Check if graph is connected (one component).

    Time Complexity: O(|V| + |E|)

    Args:
        graph: Graph to check

    Returns:
        True if graph is connected

    Examples:
        >>> graph = SimpleGraph()
        >>> graph.add_edge("A", "B")
        >>> graph.add_edge("B", "C")
        >>> is_connected(graph)
        True

        >>> graph.add_vertex("D")  # Isolated vertex
        >>> is_connected(graph)
        False
    """
    if graph.vertex_count() == 0:
        return True

    # Start BFS from first vertex
    first_vertex = next(graph.vertices()).id
    visited = set(bfs(graph, first_vertex))

    return len(visited) == graph.vertex_count()


def has_path(
    graph: BaseGraph[Any, Any],
    source: Any,
    target: Any,
) -> bool:
    """
    Check if path exists between two vertices.

    Time Complexity: O(|V| + |E|) worst case

    Args:
        graph: Graph to search
        source: Source vertex identifier
        target: Target vertex identifier

    Returns:
        True if path exists from source to target

    Examples:
        >>> graph = SimpleGraph()
        >>> graph.add_edge("A", "B")
        >>> graph.add_edge("B", "C")
        >>> has_path(graph, "A", "C")
        True
        >>> has_path(graph, "A", "D")
        False
    """
    if not graph.has_vertex(source) or not graph.has_vertex(target):
        return False

    return target in set(bfs(graph, source))


def shortest_path_bfs(
    graph: BaseGraph[Any, Any],
    source: Any,
    target: Any,
) -> list[Any] | None:
    """
    Find shortest path using BFS (unweighted graphs).

    Time Complexity: O(|V| + |E|)

    Args:
        graph: Graph to search
        source: Source vertex identifier
        target: Target vertex identifier

    Returns:
        List of vertex IDs in path from source to target, or None if no path exists

    Examples:
        >>> graph = SimpleGraph()
        >>> graph.add_edge("A", "B")
        >>> graph.add_edge("B", "C")
        >>> graph.add_edge("A", "C")
        >>> shortest_path_bfs(graph, "A", "C")
        ['A', 'C']
    """
    if not graph.has_vertex(source) or not graph.has_vertex(target):
        return None

    if source == target:
        return [source]

    visited: set[Any] = {source}
    queue: deque[tuple[Any, list[Any]]] = deque([(source, [source])])

    while queue:
        vertex, path = queue.popleft()

        for neighbor in graph.get_neighbors(vertex):
            if neighbor == target:
                return path + [neighbor]

            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, path + [neighbor]))

    return None
