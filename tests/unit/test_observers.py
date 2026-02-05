"""
Unit tests for Observer pattern implementation.
"""

from __future__ import annotations

import pytest

from packages.graphs.simple_graph import SimpleGraph
from packages.observers.change_tracker import ChangeLogger, ChangeTracker
from packages.observers.graph_observer import ConsoleObserver


class TestChangeLogger:
    """Test ChangeLogger observer."""

    @pytest.fixture
    def graph_with_logger(self) -> tuple[SimpleGraph, ChangeLogger]:
        """Create graph with attached logger."""
        graph = SimpleGraph()
        logger = ChangeLogger()
        graph.attach_observer(logger)
        return graph, logger

    def test_logs_vertex_added(
        self,
        graph_with_logger: tuple[SimpleGraph, ChangeLogger],
    ) -> None:
        """Test logging vertex additions."""
        graph, logger = graph_with_logger
        
        graph.add_vertex("A")
        graph.add_vertex("B")
        
        history = logger.get_history()
        assert len(history) == 2
        assert history[0] == ("vertex_added", ("A",))
        assert history[1] == ("vertex_added", ("B",))

    def test_logs_edge_added(
        self,
        graph_with_logger: tuple[SimpleGraph, ChangeLogger],
    ) -> None:
        """Test logging edge additions."""
        graph, logger = graph_with_logger
        
        graph.add_vertex("A")
        graph.add_vertex("B")
        graph.add_edge("A", "B", weight=5.0)
        
        history = logger.get_history()
        assert len(history) == 3
        assert history[2] == ("edge_added", ("A", "B"))

    def test_logs_vertex_removed(
        self,
        graph_with_logger: tuple[SimpleGraph, ChangeLogger],
    ) -> None:
        """Test logging vertex removal."""
        graph, logger = graph_with_logger
        
        graph.add_vertex("A")
        graph.remove_vertex("A")
        
        history = logger.get_history()
        assert history[0] == ("vertex_added", ("A",))
        assert history[1] == ("vertex_removed", ("A",))

    def test_get_last_n(
        self,
        graph_with_logger: tuple[SimpleGraph, ChangeLogger],
    ) -> None:
        """Test getting last N events."""
        graph, logger = graph_with_logger
        
        for i in range(10):
            graph.add_vertex(i)
        
        last_3 = logger.get_last_n(3)
        assert len(last_3) == 3
        assert last_3[-1] == ("vertex_added", (9,))

    def test_get_events_by_type(
        self,
        graph_with_logger: tuple[SimpleGraph, ChangeLogger],
    ) -> None:
        """Test filtering events by type."""
        graph, logger = graph_with_logger
        
        graph.add_vertex("A")
        graph.add_vertex("B")
        graph.add_edge("A", "B")
        
        vertex_events = logger.get_events_by_type("vertex_added")
        assert len(vertex_events) == 2
        assert vertex_events == [("A",), ("B",)]

    def test_clear_history(
        self,
        graph_with_logger: tuple[SimpleGraph, ChangeLogger],
    ) -> None:
        """Test clearing history."""
        graph, logger = graph_with_logger
        
        graph.add_vertex("A")
        assert logger.count() == 1
        
        logger.clear_history()
        assert logger.count() == 0

    def test_max_history_limit(self) -> None:
        """Test maximum history limit."""
        graph = SimpleGraph()
        logger = ChangeLogger(max_history=3)
        graph.attach_observer(logger)
        
        for i in range(5):
            graph.add_vertex(i)
        
        # Only last 3 events should be kept
        assert logger.count() == 3
        history = logger.get_history()
        assert history[0] == ("vertex_added", (2,))


class TestChangeTracker:
    """Test ChangeTracker observer."""

    @pytest.fixture
    def graph_with_tracker(self) -> tuple[SimpleGraph, ChangeTracker]:
        """Create graph with attached tracker."""
        graph = SimpleGraph()
        tracker = ChangeTracker()
        graph.attach_observer(tracker)
        return graph, tracker

    def test_tracks_statistics(
        self,
        graph_with_tracker: tuple[SimpleGraph, ChangeTracker],
    ) -> None:
        """Test tracking event statistics."""
        graph, tracker = graph_with_tracker
        
        graph.add_vertex("A")
        graph.add_vertex("B")
        graph.add_edge("A", "B")
        
        stats = tracker.get_statistics()
        assert stats["vertex_added"] == 2
        assert stats["edge_added"] == 1

    def test_tracks_vertex_changes(
        self,
        graph_with_tracker: tuple[SimpleGraph, ChangeTracker],
    ) -> None:
        """Test tracking vertex-specific changes."""
        graph, tracker = graph_with_tracker
        
        graph.add_vertex("A")
        graph.add_vertex("B")
        graph.add_edge("A", "B")
        
        changes_a = tracker.get_vertex_changes("A")
        assert "vertex_added" in changes_a

    def test_most_modified_vertices(
        self,
        graph_with_tracker: tuple[SimpleGraph, ChangeTracker],
    ) -> None:
        """Test finding most modified vertices."""
        graph, tracker = graph_with_tracker
        
        # Modify A more than B
        graph.add_vertex("A")
        graph.add_vertex("B")
        graph.add_vertex("C")
        graph.add_edge("A", "B")
        graph.add_edge("A", "C")
        graph.remove_edge("A", "B")
        
        most_modified = tracker.get_most_modified_vertices(top_n=2)
        assert len(most_modified) >= 1
        assert most_modified[0][0] == "A"  # A should be most modified

    def test_total_changes(
        self,
        graph_with_tracker: tuple[SimpleGraph, ChangeTracker],
    ) -> None:
        """Test counting total changes."""
        graph, tracker = graph_with_tracker
        
        graph.add_vertex("A")
        graph.add_vertex("B")
        graph.add_edge("A", "B")
        
        assert tracker.total_changes() == 3

    def test_reset(
        self,
        graph_with_tracker: tuple[SimpleGraph, ChangeTracker],
    ) -> None:
        """Test resetting tracker."""
        graph, tracker = graph_with_tracker
        
        graph.add_vertex("A")
        assert tracker.total_changes() == 1
        
        tracker.reset()
        assert tracker.total_changes() == 0


class TestConsoleObserver:
    """Test ConsoleObserver."""

    def test_console_observer(self, capsys) -> None:
        """Test console output."""
        graph = SimpleGraph()
        graph.attach_observer(ConsoleObserver())
        
        graph.add_vertex("A")
        
        captured = capsys.readouterr()
        assert "[GRAPH] vertex_added: A" in captured.out


class TestMultipleObservers:
    """Test multiple observers on same graph."""

    def test_multiple_observers(self) -> None:
        """Test attaching multiple observers."""
        graph = SimpleGraph()
        logger = ChangeLogger()
        tracker = ChangeTracker()
        
        graph.attach_observer(logger)
        graph.attach_observer(tracker)
        
        graph.add_vertex("A")
        
        assert logger.count() == 1
        assert tracker.total_changes() == 1

    def test_detach_observer(self) -> None:
        """Test detaching observers."""
        graph = SimpleGraph()
        logger = ChangeLogger()
        
        graph.attach_observer(logger)
        graph.add_vertex("A")
        assert logger.count() == 1
        
        graph.detach_observer(logger)
        graph.add_vertex("B")
        assert logger.count() == 1  # Не увеличивается после detach
