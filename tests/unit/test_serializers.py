"""
Unit tests for graph serialization.
"""

from __future__ import annotations

import json
import pickle
from pathlib import Path

import pytest

from packages.graphs.simple_graph import SimpleGraph
from packages.utils.serializers import (
    GraphIO,
    GraphSerializer,
    JSONSerializer,
    PickleSerializer,
)


class TestGraphSerializer:
    """Test base GraphSerializer."""

    @pytest.fixture
    def sample_graph(self) -> SimpleGraph:
        """Create sample graph for testing."""
        graph = SimpleGraph()
        graph.add_vertex("A", color="red", size=10)
        graph.add_vertex("B", color="blue", size=20)
        graph.add_vertex("C", color="green", size=15)
        graph.add_edge("A", "B", weight=5.0, label="edge1")
        graph.add_edge("B", "C", weight=3.0, label="edge2")
        return graph

    def test_to_dict(self, sample_graph: SimpleGraph) -> None:
        """Test converting graph to dictionary."""
        data = GraphSerializer.to_dict(sample_graph)

        assert data["graph_type"] == "SimpleGraph"
        assert data["directed"] is False
        assert len(data["vertices"]) == 3
        assert len(data["edges"]) == 2
        assert data["metadata"]["vertex_count"] == 3
        assert data["metadata"]["edge_count"] == 2

    def test_to_dict_preserves_attributes(
        self,
        sample_graph: SimpleGraph,
    ) -> None:
        """Test that vertex and edge attributes are preserved."""
        data = GraphSerializer.to_dict(sample_graph)

        # Check vertex attributes
        vertex_a = next(v for v in data["vertices"] if v["id"] == "A")
        assert vertex_a["attributes"]["color"] == "red"
        assert vertex_a["attributes"]["size"] == 10

        # Check edge attributes
        edge_ab = next(
            e for e in data["edges"] 
            if e["source"] == "A" and e["target"] == "B"
        )
        assert edge_ab["weight"] == 5.0
        assert edge_ab["attributes"]["label"] == "edge1"

    def test_from_dict(self, sample_graph: SimpleGraph) -> None:
        """Test reconstructing graph from dictionary."""
        data = GraphSerializer.to_dict(sample_graph)
        restored = GraphSerializer.from_dict(data)

        assert isinstance(restored, SimpleGraph)
        assert restored.vertex_count() == 3
        assert restored.edge_count() == 2
        assert restored.has_vertex("A")
        assert restored.has_edge("A", "B")

    def test_roundtrip_preserves_structure(
        self,
        sample_graph: SimpleGraph,
    ) -> None:
        """Test that serialize->deserialize preserves graph structure."""
        data = GraphSerializer.to_dict(sample_graph)
        restored = GraphSerializer.from_dict(data)

        # Check vertices
        assert set(v.id for v in restored.vertices()) == {"A", "B", "C"}

        # Check edges
        assert restored.has_edge("A", "B")
        assert restored.has_edge("B", "C")
        assert not restored.has_edge("A", "C")

    def test_from_dict_invalid_type_raises(self) -> None:
        """Test that invalid graph type raises error."""
        data = {
            "graph_type": "InvalidGraph",
            "directed": False,
            "vertices": [],
            "edges": [],
        }

        with pytest.raises(ValueError, match="Unsupported graph type"):
            GraphSerializer.from_dict(data)


class TestJSONSerializer:
    """Test JSON serialization."""

    @pytest.fixture
    def sample_graph(self) -> SimpleGraph:
        """Create sample graph."""
        graph = SimpleGraph()
        graph.add_vertex("A", priority=1)
        graph.add_vertex("B", priority=2)
        graph.add_edge("A", "B", weight=10.0)
        return graph

    @pytest.fixture
    def temp_json_file(self, tmp_path: Path) -> Path:
        """Create temporary JSON file path."""
        return tmp_path / "test_graph.json"

    def test_save_and_load(
        self,
        sample_graph: SimpleGraph,
        temp_json_file: Path,
    ) -> None:
        """Test saving and loading JSON file."""
        # Save
        JSONSerializer.save(sample_graph, temp_json_file)
        assert temp_json_file.exists()

        # Load
        loaded = JSONSerializer.load(temp_json_file)
        assert isinstance(loaded, SimpleGraph)
        assert loaded.vertex_count() == 2
        assert loaded.edge_count() == 1

    def test_json_is_valid(
        self,
        sample_graph: SimpleGraph,
        temp_json_file: Path,
    ) -> None:
        """Test that saved JSON is valid and readable."""
        JSONSerializer.save(sample_graph, temp_json_file)

        # Read and parse JSON directly
        with temp_json_file.open("r") as f:
            data = json.load(f)

        assert "graph_type" in data
        assert "vertices" in data
        assert "edges" in data

    def test_dumps_and_loads(self, sample_graph: SimpleGraph) -> None:
        """Test string serialization."""
        # Serialize to string
        json_str = JSONSerializer.dumps(sample_graph)
        assert isinstance(json_str, str)
        assert "SimpleGraph" in json_str

        # Deserialize from string
        loaded = JSONSerializer.loads(json_str)
        assert isinstance(loaded, SimpleGraph)
        assert loaded.vertex_count() == 2

    def test_indent_parameter(
        self,
        sample_graph: SimpleGraph,
        temp_json_file: Path,
    ) -> None:
        """Test JSON indentation."""
        # Save with indentation
        JSONSerializer.save(sample_graph, temp_json_file, indent=4)
        indented_size = temp_json_file.stat().st_size

        # Save without indentation (compact)
        JSONSerializer.save(sample_graph, temp_json_file, indent=None)
        compact_size = temp_json_file.stat().st_size

        # Indented should be larger
        assert indented_size > compact_size

    def test_unicode_handling(self, tmp_path: Path) -> None:
        """Test Unicode characters in vertex IDs and attributes."""
        graph = SimpleGraph()
        graph.add_vertex("Москва", country="Россия")
        graph.add_vertex("北京", country="中国")
        graph.add_edge("Москва", "北京", weight=7000.0)

        filepath = tmp_path / "unicode.json"
        JSONSerializer.save(graph, filepath)

        loaded = JSONSerializer.load(filepath)
        assert loaded.has_vertex("Москва")
        assert loaded.has_vertex("北京")


class TestPickleSerializer:
    """Test Pickle serialization."""

    @pytest.fixture
    def sample_graph(self) -> SimpleGraph:
        """Create sample graph."""
        graph = SimpleGraph()
        graph.add_vertex("X")
        graph.add_vertex("Y")
        graph.add_vertex("Z")
        graph.add_edge("X", "Y", weight=1.5)
        graph.add_edge("Y", "Z", weight=2.5)
        return graph

    @pytest.fixture
    def temp_pickle_file(self, tmp_path: Path) -> Path:
        """Create temporary pickle file path."""
        return tmp_path / "test_graph.pkl"

    def test_save_and_load(
        self,
        sample_graph: SimpleGraph,
        temp_pickle_file: Path,
    ) -> None:
        """Test saving and loading pickle file."""
        # Save
        PickleSerializer.save(sample_graph, temp_pickle_file)
        assert temp_pickle_file.exists()

        # Load
        loaded = PickleSerializer.load(temp_pickle_file)
        assert isinstance(loaded, SimpleGraph)
        assert loaded.vertex_count() == 3
        assert loaded.edge_count() == 2

    def test_dumps_and_loads(self, sample_graph: SimpleGraph) -> None:
        """Test bytes serialization."""
        # Serialize to bytes
        data = PickleSerializer.dumps(sample_graph)
        assert isinstance(data, bytes)
        assert len(data) > 0

        # Deserialize from bytes
        loaded = PickleSerializer.loads(data)
        assert isinstance(loaded, SimpleGraph)
        assert loaded.vertex_count() == 3

    def test_pickle_preserves_exact_state(
        self,
        sample_graph: SimpleGraph,
        temp_pickle_file: Path,
    ) -> None:
        """Test that pickle preserves exact graph state."""
        # Add complex attributes
        sample_graph.add_vertex("W", data=[1, 2, 3], nested={"key": "value"})

        # Save and load
        PickleSerializer.save(sample_graph, temp_pickle_file)
        loaded = PickleSerializer.load(temp_pickle_file)

        # Check complex attributes preserved
        vertex_w = loaded.get_vertex("W")
        assert vertex_w.attributes["data"] == [1, 2, 3]
        assert vertex_w.attributes["nested"] == {"key": "value"}

    def test_pickle_smaller_than_json(
        self,
        sample_graph: SimpleGraph,
        tmp_path: Path,
    ) -> None:
        """Test that pickle is typically smaller than JSON."""
        json_path = tmp_path / "graph.json"
        pickle_path = tmp_path / "graph.pkl"

        JSONSerializer.save(sample_graph, json_path)
        PickleSerializer.save(sample_graph, pickle_path)

        json_size = json_path.stat().st_size
        pickle_size = pickle_path.stat().st_size

        # Pickle is usually more compact (not always, but typically)
        assert pickle_size <= json_size * 1.5  # Allow some variance


class TestGraphIO:
    """Test GraphIO convenience interface."""

    @pytest.fixture
    def sample_graph(self) -> SimpleGraph:
        """Create sample graph."""
        graph = SimpleGraph()
        graph.add_vertex("Node1")
        graph.add_vertex("Node2")
        graph.add_edge("Node1", "Node2", weight=42.0)
        return graph

    def test_save_load_json(
        self,
        sample_graph: SimpleGraph,
        tmp_path: Path,
    ) -> None:
        """Test GraphIO with JSON format."""
        filepath = tmp_path / "graph.json"

        GraphIO.save(sample_graph, filepath)
        loaded = GraphIO.load(filepath)

        assert isinstance(loaded, SimpleGraph)
        assert loaded.vertex_count() == 2

    def test_save_load_pickle(
        self,
        sample_graph: SimpleGraph,
        tmp_path: Path,
    ) -> None:
        """Test GraphIO with Pickle format."""
        filepath = tmp_path / "graph.pkl"

        GraphIO.save(sample_graph, filepath)
        loaded = GraphIO.load(filepath)

        assert isinstance(loaded, SimpleGraph)
        assert loaded.vertex_count() == 2

    def test_unsupported_extension_raises(
        self,
        sample_graph: SimpleGraph,
        tmp_path: Path,
    ) -> None:
        """Test that unsupported extension raises error."""
        filepath = tmp_path / "graph.txt"

        with pytest.raises(ValueError, match="Unsupported format"):
            GraphIO.save(sample_graph, filepath)

        # Create empty file
        filepath.touch()

        with pytest.raises(ValueError, match="Unsupported format"):
            GraphIO.load(filepath)

    def test_pickle_extension(
        self,
        sample_graph: SimpleGraph,
        tmp_path: Path,
    ) -> None:
        """Test that .pickle extension also works."""
        filepath = tmp_path / "graph.pickle"

        GraphIO.save(sample_graph, filepath)
        loaded = GraphIO.load(filepath)

        assert isinstance(loaded, SimpleGraph)


class TestConvenienceFunctions:
    """Test module-level convenience functions."""

    def test_save_and_load_graph(self, tmp_path: Path) -> None:
        """Test save_graph and load_graph functions."""
        from packages.utils.serializers import load_graph, save_graph

        graph = SimpleGraph()
        graph.add_vertex("Test")

        filepath = tmp_path / "convenience.json"
        save_graph(graph, filepath)

        loaded = load_graph(filepath)
        assert loaded.has_vertex("Test")


class TestEdgeCases:
    """Test edge cases and special scenarios."""

    def test_empty_graph(self, tmp_path: Path) -> None:
        """Test serializing empty graph."""
        graph = SimpleGraph()

        filepath = tmp_path / "empty.json"
        JSONSerializer.save(graph, filepath)

        loaded = JSONSerializer.load(filepath)
        assert loaded.vertex_count() == 0
        assert loaded.edge_count() == 0

    def test_directed_graph(self, tmp_path: Path) -> None:
        """Test serializing directed graph."""
        graph = SimpleGraph(directed=True)
        graph.add_vertex("A")
        graph.add_vertex("B")
        graph.add_edge("A", "B", weight=1.0)

        filepath = tmp_path / "directed.json"
        JSONSerializer.save(graph, filepath)

        loaded = JSONSerializer.load(filepath)
        assert loaded._directed is True
        assert loaded.has_edge("A", "B")

    def test_different_representations(self, tmp_path: Path) -> None:
        """Test graphs with different representations."""
        for repr_type in ["adjacency_list", "adjacency_matrix", "edge_list"]:
            graph = SimpleGraph(representation=repr_type)
            graph.add_vertex("X")
            graph.add_vertex("Y")
            graph.add_edge("X", "Y")

            filepath = tmp_path / f"{repr_type}.json"
            JSONSerializer.save(graph, filepath)

            loaded = JSONSerializer.load(filepath)
            assert loaded.vertex_count() == 2
            assert loaded.edge_count() == 1

    def test_large_graph_performance(self, tmp_path: Path) -> None:
        """Test serializing larger graph (performance check)."""
        graph = SimpleGraph()

        # Add 1000 vertices
        for i in range(1000):
            graph.add_vertex(i)

        # Add 2000 edges
        for i in range(2000):
            source = i % 1000
            target = (i + 1) % 1000
            if not graph.has_edge(source, target):
                graph.add_edge(source, target, weight=float(i))

        # Test JSON
        json_path = tmp_path / "large.json"
        JSONSerializer.save(graph, json_path)
        loaded_json = JSONSerializer.load(json_path)
        assert loaded_json.vertex_count() == 1000

        # Test Pickle
        pickle_path = tmp_path / "large.pkl"
        PickleSerializer.save(graph, pickle_path)
        loaded_pickle = PickleSerializer.load(pickle_path)
        assert loaded_pickle.vertex_count() == 1000
