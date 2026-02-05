"""
Advanced change tracking with history and statistics.

This module provides observers that collect detailed information about
graph modifications over time.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from typing import Any

from packages.observers.graph_observer import GraphObserver


class ChangeLogger(GraphObserver):
    """
    Observer that logs all graph changes to a history list.

    Useful for debugging, undo/redo functionality, and auditing.

    Examples:
        >>> logger = ChangeLogger()
        >>> graph.attach_observer(logger)
        >>> 
        >>> graph.add_vertex("A")
        >>> graph.add_vertex("B")
        >>> graph.add_edge("A", "B")
        >>> 
        >>> logger.get_history()
        [
            ('vertex_added', ('A',)),
            ('vertex_added', ('B',)),
            ('edge_added', ('A', 'B'))
        ]
        >>> 
        >>> logger.count()
        3
    """

    def __init__(self, max_history: int | None = None) -> None:
        """
        Initialize change logger.

        Args:
            max_history: Maximum number of events to store (None = unlimited)
        """
        self._history: list[tuple[str, tuple[Any, ...]]] = []
        self._max_history = max_history

    def update(self, event: str, *args: Any, **kwargs: Any) -> None:
        """Log the change event."""
        self._history.append((event, args))
        
        # Enforce max history limit
        if self._max_history and len(self._history) > self._max_history:
            self._history = self._history[-self._max_history:]

    def get_history(self) -> list[tuple[str, tuple[Any, ...]]]:
        """
        Get full change history.

        Returns:
            List of (event_name, args_tuple) pairs
        """
        return self._history.copy()

    def get_last_n(self, n: int) -> list[tuple[str, tuple[Any, ...]]]:
        """
        Get last N events.

        Args:
            n: Number of recent events to retrieve

        Returns:
            List of recent events
        """
        return self._history[-n:]

    def get_events_by_type(self, event_type: str) -> list[tuple[Any, ...]]:
        """
        Get all events of a specific type.

        Args:
            event_type: Event name to filter by

        Returns:
            List of argument tuples for matching events

        Examples:
            >>> logger.get_events_by_type("vertex_added")
            [('A',), ('B',), ('C',)]
        """
        return [args for event, args in self._history if event == event_type]

    def count(self) -> int:
        """
        Get total number of logged events.

        Returns:
            Number of events in history
        """
        return len(self._history)

    def clear_history(self) -> None:
        """Clear all logged events."""
        self._history.clear()

    def __repr__(self) -> str:
        """String representation."""
        return f"ChangeLogger(events={len(self._history)})"

    def __len__(self) -> int:
        """Return number of logged events."""
        return len(self._history)


class ChangeTracker(GraphObserver):
    """
    Observer that tracks detailed statistics about graph changes.

    Provides aggregated metrics and analysis of modification patterns.

    Examples:
        >>> tracker = ChangeTracker()
        >>> graph.attach_observer(tracker)
        >>> 
        >>> # ... make changes ...
        >>> 
        >>> tracker.get_statistics()
        {
            'vertex_added': 10,
            'edge_added': 15,
            'edge_removed': 2
        }
        >>> 
        >>> tracker.get_vertex_changes("A")
        ['vertex_added', 'edge_added', 'edge_removed']
        >>> 
        >>> tracker.get_most_modified_vertices(top_n=3)
        [('A', 5), ('B', 3), ('C', 2)]
    """

    def __init__(self) -> None:
        """Initialize change tracker."""
        self._event_counts: Counter[str] = Counter()
        self._vertex_changes: dict[Any, list[str]] = defaultdict(list)
        self._edge_changes: list[tuple[str, Any, Any]] = []
        self._timeline: list[tuple[str, tuple[Any, ...]]] = []

    def update(self, event: str, *args: Any, **kwargs: Any) -> None:
        """Track the change event with detailed analysis."""
        # Count event type
        self._event_counts[event] += 1
        
        # Add to timeline
        self._timeline.append((event, args))

        # Track vertex-specific changes
        if "vertex" in event and args:
            vertex_id = args[0]
            self._vertex_changes[vertex_id].append(event)

        # Track edge-specific changes
        if "edge" in event and len(args) >= 2:
            self._edge_changes.append((event, args[0], args[1]))

    def get_statistics(self) -> dict[str, int]:
        """
        Get aggregated event statistics.

        Returns:
            Dictionary mapping event type to count

        Examples:
            >>> tracker.get_statistics()
            {'vertex_added': 5, 'edge_added': 8, 'edge_removed': 1}
        """
        return dict(self._event_counts)

    def get_vertex_changes(self, vertex_id: Any) -> list[str]:
        """
        Get all change events for a specific vertex.

        Args:
            vertex_id: Vertex to get changes for

        Returns:
            List of event names affecting this vertex

        Examples:
            >>> tracker.get_vertex_changes("A")
            ['vertex_added', 'edge_added', 'edge_added']
        """
        return self._vertex_changes[vertex_id].copy()

    def get_most_modified_vertices(self, top_n: int = 5) -> list[tuple[Any, int]]:
        """
        Get vertices with most modifications.

        Args:
            top_n: Number of top vertices to return

        Returns:
            List of (vertex_id, modification_count) tuples, sorted by count

        Examples:
            >>> tracker.get_most_modified_vertices(top_n=3)
            [('A', 10), ('B', 7), ('C', 5)]
        """
        vertex_counts = {
            vid: len(changes) 
            for vid, changes in self._vertex_changes.items()
        }
        sorted_vertices = sorted(
            vertex_counts.items(), 
            key=lambda x: x[1], 
            reverse=True
        )
        return sorted_vertices[:top_n]

    def get_edge_modifications(self) -> list[tuple[str, Any, Any]]:
        """
        Get all edge modification events.

        Returns:
            List of (event, source, target) tuples

        Examples:
            >>> tracker.get_edge_modifications()
            [
                ('edge_added', 'A', 'B'),
                ('edge_added', 'B', 'C'),
                ('edge_removed', 'A', 'B')
            ]
        """
        return self._edge_changes.copy()

    def total_changes(self) -> int:
        """
        Get total number of change events.

        Returns:
            Total count of all events
        """
        return sum(self._event_counts.values())

    def get_timeline(self) -> list[tuple[str, tuple[Any, ...]]]:
        """
        Get chronological timeline of all events.

        Returns:
            List of (event, args) tuples in order of occurrence
        """
        return self._timeline.copy()

    def reset(self) -> None:
        """Reset all tracked statistics."""
        self._event_counts.clear()
        self._vertex_changes.clear()
        self._edge_changes.clear()
        self._timeline.clear()

    def __repr__(self) -> str:
        """String representation."""
        return f"ChangeTracker(total_changes={self.total_changes()})"

    def __str__(self) -> str:
        """Human-readable string."""
        stats = self.get_statistics()
        stats_str = ", ".join(f"{k}={v}" for k, v in sorted(stats.items()))
        return f"ChangeTracker({stats_str})"
