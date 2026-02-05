"""
Serialization utilities for graphs.

Supports JSON and Pickle formats with full graph state preservation.
"""

from __future__ import annotations

import json
import pickle
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from packages.core.base_graph import BaseGraph


class GraphSerializer:
    """
    Base serializer for graph objects.

    Provides common interface for different serialization formats.
    """

    @staticmethod
    def to_dict(graph: BaseGraph) -> dict[str, Any]:
        """
        Convert graph to dictionary representation.

        Args:
            graph: Graph to serialize

        Returns:
            Dictionary with complete graph state

        Examples:
            >>> graph = SimpleGraph()
            >>> graph.add_vertex("A", color="red")
            >>> data = GraphSerializer.to_dict(graph)
            >>> data["vertices"]
            [{"id": "A", "attributes": {"color": "red"}}]
        """
        # Collect vertices
        vertices = []
        for vertex in graph.vertices():
            vertices.append({
                "id": vertex.id,
                "attributes": vertex.attributes.copy(),
            })

        # Collect edges
        edges = []
        for edge in graph.edges():
            edges.append({
                "source": edge.source,
                "target": edge.target,
                "weight": edge.weight,
                "directed": edge.directed,
                "attributes": edge.attributes.copy(),
            })

        # Graph metadata
        return {
            "graph_type": graph.__class__.__name__,
            "directed": graph._directed,
            "representation": graph._representation.__class__.__name__,
            "vertices": vertices,
            "edges": edges,
            "metadata": {
                "vertex_count": graph.vertex_count(),
                "edge_count": graph.edge_count(),
            },
        }

    @staticmethod
    def from_dict(data: dict[str, Any]) -> BaseGraph:
        """
        Reconstruct graph from dictionary.

        Args:
            data: Dictionary with graph state

        Returns:
            Reconstructed graph instance

        Raises:
            ValueError: If graph_type is not supported

        Examples:
            >>> data = {"graph_type": "SimpleGraph", ...}
            >>> graph = GraphSerializer.from_dict(data)
        """
        from packages.graphs.hypergraph import Hypergraph
        from packages.graphs.multigraph import Multigraph
        from packages.graphs.pseudograph import Pseudograph
        from packages.graphs.simple_graph import SimpleGraph

        # Map graph types
        graph_types = {
            "SimpleGraph": SimpleGraph,
            "Multigraph": Multigraph,
            "Pseudograph": Pseudograph,
            "Hypergraph": Hypergraph,
        }

        graph_type = data.get("graph_type")
        if graph_type not in graph_types:
            supported = ", ".join(graph_types.keys())
            msg = f"Unsupported graph type: {graph_type!r}. Supported: {supported}"
            raise ValueError(msg)

        # Create graph instance
        graph_class = graph_types[graph_type]
        
        # Map representation names
        repr_map = {
            "AdjacencyListRepresentation": "adjacency_list",
            "AdjacencyMatrixRepresentation": "adjacency_matrix",
            "EdgeListRepresentation": "edge_list",
        }
        
        repr_name = data.get("representation", "AdjacencyListRepresentation")
        repr_type = repr_map.get(repr_name, "adjacency_list")
        
        graph = graph_class(
            directed=data.get("directed", False),
            representation=repr_type,
        )

        # Restore vertices
        for vertex_data in data.get("vertices", []):
            graph.add_vertex(
                vertex_data["id"],
                **vertex_data.get("attributes", {}),
            )

        # Restore edges
        for edge_data in data.get("edges", []):
            if graph_type == "Hypergraph":
                # Hypergraph edges need special handling
                # For now, skip or implement hyperedge restoration
                pass
            else:
                graph.add_edge(
                    edge_data["source"],
                    edge_data["target"],
                    weight=edge_data.get("weight", 1.0),
                    **edge_data.get("attributes", {}),
                )

        return graph


class JSONSerializer:
    """
    JSON serialization for graphs.

    Provides human-readable format, good for configuration and data exchange.

    Examples:
        >>> graph = SimpleGraph()
        >>> graph.add_vertex("A")
        >>> JSONSerializer.save(graph, "graph.json")
        >>> loaded = JSONSerializer.load("graph.json")
    """

    @staticmethod
    def save(graph: BaseGraph, filepath: str | Path, *, indent: int = 2) -> None:
        """
        Save graph to JSON file.

        Args:
            graph: Graph to save
            filepath: Path to output file
            indent: JSON indentation level (default: 2)

        Examples:
            >>> JSONSerializer.save(graph, "output.json")
            >>> JSONSerializer.save(graph, "compact.json", indent=None)
        """
        filepath = Path(filepath)
        data = GraphSerializer.to_dict(graph)

        with filepath.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=indent, ensure_ascii=False)

    @staticmethod
    def load(filepath: str | Path) -> BaseGraph:
        """
        Load graph from JSON file.

        Args:
            filepath: Path to input file

        Returns:
            Loaded graph instance

        Raises:
            FileNotFoundError: If file doesn't exist
            json.JSONDecodeError: If file is not valid JSON

        Examples:
            >>> graph = JSONSerializer.load("graph.json")
        """
        filepath = Path(filepath)

        with filepath.open("r", encoding="utf-8") as f:
            data = json.load(f)

        return GraphSerializer.from_dict(data)

    @staticmethod
    def dumps(graph: BaseGraph, *, indent: int = 2) -> str:
        """
        Serialize graph to JSON string.

        Args:
            graph: Graph to serialize
            indent: JSON indentation level

        Returns:
            JSON string

        Examples:
            >>> json_str = JSONSerializer.dumps(graph)
            >>> print(json_str)
        """
        data = GraphSerializer.to_dict(graph)
        return json.dumps(data, indent=indent, ensure_ascii=False)

    @staticmethod
    def loads(json_str: str) -> BaseGraph:
        """
        Deserialize graph from JSON string.

        Args:
            json_str: JSON string to parse

        Returns:
            Graph instance

        Examples:
            >>> graph = JSONSerializer.loads('{"graph_type": "SimpleGraph", ...}')
        """
        data = json.loads(json_str)
        return GraphSerializer.from_dict(data)


class PickleSerializer:
    """
    Pickle serialization for graphs.

    Binary format, fastest and most compact. Preserves all Python objects.

    ⚠️ Warning: Only load pickle files from trusted sources!

    Examples:
        >>> graph = SimpleGraph()
        >>> PickleSerializer.save(graph, "graph.pkl")
        >>> loaded = PickleSerializer.load("graph.pkl")
    """

    @staticmethod
    def save(
        graph: BaseGraph,
        filepath: str | Path,
        *,
        protocol: int = pickle.HIGHEST_PROTOCOL,
    ) -> None:
        """
        Save graph to pickle file.

        Args:
            graph: Graph to save
            filepath: Path to output file
            protocol: Pickle protocol version (default: highest available)

        Examples:
            >>> PickleSerializer.save(graph, "graph.pkl")
        """
        filepath = Path(filepath)

        with filepath.open("wb") as f:
            pickle.dump(graph, f, protocol=protocol)

    @staticmethod
    def load(filepath: str | Path) -> BaseGraph:
        """
        Load graph from pickle file.

        Args:
            filepath: Path to input file

        Returns:
            Loaded graph instance

        Raises:
            FileNotFoundError: If file doesn't exist
            pickle.UnpicklingError: If file is corrupted

        Examples:
            >>> graph = PickleSerializer.load("graph.pkl")
        """
        filepath = Path(filepath)

        with filepath.open("rb") as f:
            return pickle.load(f)

    @staticmethod
    def dumps(graph: BaseGraph, *, protocol: int = pickle.HIGHEST_PROTOCOL) -> bytes:
        """
        Serialize graph to pickle bytes.

        Args:
            graph: Graph to serialize
            protocol: Pickle protocol version

        Returns:
            Pickled bytes

        Examples:
            >>> data = PickleSerializer.dumps(graph)
            >>> len(data)
            1234
        """
        return pickle.dumps(graph, protocol=protocol)

    @staticmethod
    def loads(data: bytes) -> BaseGraph:
        """
        Deserialize graph from pickle bytes.

        Args:
            data: Pickled bytes

        Returns:
            Graph instance

        Examples:
            >>> graph = PickleSerializer.loads(data)
        """
        return pickle.loads(data)


class GraphIO:
    """
    Convenience interface for graph I/O operations.

    Auto-detects format from file extension.

    Examples:
        >>> # Save
        >>> GraphIO.save(graph, "graph.json")  # Auto-uses JSON
        >>> GraphIO.save(graph, "graph.pkl")   # Auto-uses Pickle
        >>> 
        >>> # Load
        >>> graph = GraphIO.load("graph.json")
        >>> graph = GraphIO.load("graph.pkl")
    """

    @staticmethod
    def save(graph: BaseGraph, filepath: str | Path, **kwargs: Any) -> None:
        """
        Save graph to file (auto-detect format).

        Args:
            graph: Graph to save
            filepath: Output file path (.json or .pkl)
            **kwargs: Additional arguments for serializer

        Raises:
            ValueError: If file extension is not supported

        Examples:
            >>> GraphIO.save(graph, "output.json")
            >>> GraphIO.save(graph, "output.pkl")
        """
        filepath = Path(filepath)
        suffix = filepath.suffix.lower()

        if suffix == ".json":
            JSONSerializer.save(graph, filepath, **kwargs)
        elif suffix in {".pkl", ".pickle"}:
            PickleSerializer.save(graph, filepath, **kwargs)
        else:
            msg = f"Unsupported format: {suffix}. Use .json or .pkl"
            raise ValueError(msg)

    @staticmethod
    def load(filepath: str | Path) -> BaseGraph:
        """
        Load graph from file (auto-detect format).

        Args:
            filepath: Input file path

        Returns:
            Loaded graph

        Raises:
            ValueError: If file extension is not supported

        Examples:
            >>> graph = GraphIO.load("input.json")
            >>> graph = GraphIO.load("input.pkl")
        """
        filepath = Path(filepath)
        suffix = filepath.suffix.lower()

        if suffix == ".json":
            return JSONSerializer.load(filepath)
        elif suffix in {".pkl", ".pickle"}:
            return PickleSerializer.load(filepath)
        else:
            msg = f"Unsupported format: {suffix}. Use .json or .pkl"
            raise ValueError(msg)


# Convenience functions at module level
def save_graph(graph: BaseGraph, filepath: str | Path, **kwargs: Any) -> None:
    """
    Save graph to file (convenience function).

    Args:
        graph: Graph to save
        filepath: Output path
        **kwargs: Additional serializer arguments

    Examples:
        >>> from packages.utils.serializers import save_graph
        >>> save_graph(graph, "output.json")
    """
    GraphIO.save(graph, filepath, **kwargs)


def load_graph(filepath: str | Path) -> BaseGraph:
    """
    Load graph from file (convenience function).

    Args:
        filepath: Input path

    Returns:
        Loaded graph

    Examples:
        >>> from packages.utils.serializers import load_graph
        >>> graph = load_graph("input.json")
    """
    return GraphIO.load(filepath)
