"""
Graph serialization to JSON, Pickle, and other formats.
"""

from __future__ import annotations

import json
import pickle
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from packages.core.base_graph import BaseGraph


def graph_to_dict(graph: BaseGraph[Any, Any]) -> dict[str, Any]:
    """
    Convert graph to dictionary representation.

    Args:
        graph: Graph to serialize

    Returns:
        Dictionary with vertices and edges

    Examples:
        >>> graph = SimpleGraph()
        >>> graph.add_vertex("A", color="red")
        >>> graph.add_edge("A", "B", weight=5.0)
        >>> data = graph_to_dict(graph)
        >>> data['vertices']
        [{'id': 'A', 'attributes': {'color': 'red'}}, ...]
    """
    vertices = []
    for vertex in graph.vertices():
        vertices.append({"id": vertex.id, "attributes": vertex.attributes})

    edges = []
    for edge in graph.edges():
        edges.append({
            "source": edge.source,
            "target": edge.target,
            "weight": edge.weight,
            "directed": edge.directed,
            "attributes": edge.attributes,
        })

    return {
        "graph_type": graph.__class__.__name__,
        "directed": graph.is_directed(),
        "vertices": vertices,
        "edges": edges,
        "metadata": getattr(graph, "_metadata", {}),
    }


def graph_to_json(graph: BaseGraph[Any, Any], filepath: str | Path) -> None:
    """
    Save graph to JSON file.

    Args:
        graph: Graph to save
        filepath: Output file path

    Examples:
        >>> graph_to_json(graph, "my_graph.json")
    """
    data = graph_to_dict(graph)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def graph_from_json(filepath: str | Path) -> dict[str, Any]:
    """
    Load graph data from JSON file.

    Args:
        filepath: Input file path

    Returns:
        Dictionary with graph data

    Examples:
        >>> data = graph_from_json("my_graph.json")
        >>> # Reconstruct graph from data
    """
    with open(filepath, encoding="utf-8") as f:
        return json.load(f)


def graph_to_pickle(graph: BaseGraph[Any, Any], filepath: str | Path) -> None:
    """
    Save graph to Pickle file (fast, binary).

    Args:
        graph: Graph to save
        filepath: Output file path

    Examples:
        >>> graph_to_pickle(graph, "my_graph.pkl")
    """
    with open(filepath, "wb") as f:
        pickle.dump(graph, f, protocol=pickle.HIGHEST_PROTOCOL)


def graph_from_pickle(filepath: str | Path) -> BaseGraph[Any, Any]:
    """
    Load graph from Pickle file.

    Args:
        filepath: Input file path

    Returns:
        Reconstructed graph object

    Examples:
        >>> graph = graph_from_pickle("my_graph.pkl")
    """
    with open(filepath, "rb") as f:
        return pickle.load(f)
