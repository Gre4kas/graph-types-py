"""
Graph type converters implementing Adapter pattern.

This module provides utilities to convert between different graph types
while preserving as much structure as possible.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from packages.graphs.multigraph import Multigraph
    from packages.graphs.pseudograph import Pseudograph
    from packages.graphs.simple_graph import SimpleGraph


def simple_to_multigraph(simple: SimpleGraph) -> Multigraph:
    """
    Convert simple graph to multigraph.

    All edges are preserved. Multigraph allows adding duplicate edges later.

    Args:
        simple: Source simple graph

    Returns:
        New Multigraph instance

    Examples:
        >>> simple = SimpleGraph()
        >>> simple.add_edge("A", "B")
        >>> multi = simple_to_multigraph(simple)
        >>> multi.add_edge("A", "B")  # Now allowed
    """
    from packages.graphs.multigraph import Multigraph

    multi = Multigraph(directed=simple.is_directed())

    # Copy vertices
    for vertex in simple.vertices():
        multi.add_vertex(vertex.id, **vertex.attributes)

    # Copy edges
    for edge in simple.edges():
        multi.add_edge(edge.source, edge.target, weight=edge.weight, **edge.attributes)

    return multi


def multigraph_to_simple(multi: Multigraph, *, merge_strategy: str = "min") -> SimpleGraph:
    """
    Convert multigraph to simple graph by merging parallel edges.

    Args:
        multi: Source multigraph
        merge_strategy: How to merge parallel edges:
            - "min": Keep edge with minimum weight (default)
            - "max": Keep edge with maximum weight
            - "sum": Sum weights of parallel edges
            - "avg": Average weights of parallel edges

    Returns:
        New SimpleGraph instance

    Raises:
        ValueError: If merge_strategy is invalid

    Examples:
        >>> multi = Multigraph()
        >>> multi.add_edge("A", "B", weight=3.0)
        >>> multi.add_edge("A", "B", weight=5.0)
        >>> simple = multigraph_to_simple(multi, merge_strategy="min")
        >>> edge = next(simple.edges())
        >>> edge.weight
        3.0
    """
    from packages.graphs.simple_graph import SimpleGraph

    if merge_strategy not in {"min", "max", "sum", "avg"}:
        msg = f"Invalid merge_strategy: {merge_strategy!r}"
        raise ValueError(msg)

    simple = SimpleGraph(directed=multi.is_directed())

    # Copy vertices
    for vertex in multi.vertices():
        simple.add_vertex(vertex.id, **vertex.attributes)

    # Merge parallel edges
    edge_weights: dict[tuple[Any, Any], list[float]] = {}

    for edge in multi.edges():
        key = (edge.source, edge.target)
        if key not in edge_weights:
            edge_weights[key] = []
        edge_weights[key].append(edge.weight)

    # Apply merge strategy
    for (source, target), weights in edge_weights.items():
        if merge_strategy == "min":
            weight = min(weights)
        elif merge_strategy == "max":
            weight = max(weights)
        elif merge_strategy == "sum":
            weight = sum(weights)
        elif merge_strategy == "avg":
            weight = sum(weights) / len(weights)

        simple.add_edge(source, target, weight=weight)

    return simple


def pseudograph_to_simple(
    pseudo: Pseudograph,
    *,
    remove_loops: bool = True,
    merge_strategy: str = "min",
) -> SimpleGraph:
    """
    Convert pseudograph to simple graph by removing loops and merging parallel edges.

    Args:
        pseudo: Source pseudograph
        remove_loops: Whether to remove self-loops (default: True)
        merge_strategy: How to merge parallel edges (see multigraph_to_simple)

    Returns:
        New SimpleGraph instance

    Examples:
        >>> pseudo = Pseudograph()
        >>> pseudo.add_edge("A", "A", weight=1.0)  # Self-loop
        >>> pseudo.add_edge("A", "B", weight=3.0)
        >>> pseudo.add_edge("A", "B", weight=5.0)
        >>> simple = pseudograph_to_simple(pseudo)
        >>> simple.has_edge("A", "A")
        False
        >>> edge = next(e for e in simple.edges() if e.source == "A" and e.target == "B")
        >>> edge.weight
        3.0
    """
    from packages.graphs.simple_graph import SimpleGraph

    simple = SimpleGraph(directed=pseudo.is_directed())

    # Copy vertices
    for vertex in pseudo.vertices():
        simple.add_vertex(vertex.id, **vertex.attributes)

    # Merge edges, excluding self-loops
    edge_weights: dict[tuple[Any, Any], list[float]] = {}

    for edge in pseudo.edges():
        # Skip self-loops if requested
        if remove_loops and edge.is_self_loop():
            continue

        key = (edge.source, edge.target)
        if key not in edge_weights:
            edge_weights[key] = []
        edge_weights[key].append(edge.weight)

    # Apply merge strategy
    merge_funcs = {
        "min": min,
        "max": max,
        "sum": sum,
        "avg": lambda ws: sum(ws) / len(ws),
    }

    merge_func = merge_funcs[merge_strategy]

    for (source, target), weights in edge_weights.items():
        weight = merge_func(weights)
        simple.add_edge(source, target, weight=weight)

    return simple
