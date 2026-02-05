"""
Advanced change tracking with statistics.
"""

from __future__ import annotations

from collections import Counter
from typing import Any

from packages.observers.graph_observer import GraphObserver


class ChangeTracker(GraphObserver):
    """
    Observer that tracks statistics about graph changes.

    Examples:
        >>> tracker = ChangeTracker()
        >>> graph.attach_observer(tracker)
        >>> # ... make changes ...
        >>> tracker.get_statistics()
        {'vertex_added': 10, 'edge_added': 15, ...}
    """

    def __init__(self) -> None:
        """Initialize change tracker."""
        self._event_counts: Counter[str] = Counter()
        self._vertex_changes: dict[Any, list[str]] = {}
        self._edge_changes: list[tuple[str, Any, Any]] = []

    def update(self, event: str, *args: Any, **kwargs: Any) -> None:
        """Track the change."""
        self._event_counts[event] += 1

        # Track vertex-specific changes
        if "vertex" in event and args:
            vertex_id = args[0]
            if vertex_id not in self._vertex_changes:
                self._vertex_changes[vertex_id] = []
            self._vertex_changes[vertex_id].append(event)

        # Track edge-specific changes
        if "edge" in event and len(args) >= 2:
            self._edge_changes.append((event, args[0], args[1]))

    def get_statistics(self) -> dict[str, int]:
        """Get event statistics."""
        return dict(self._event_counts)

    def get_vertex_changes(self, vertex_id: Any) -> list[str]:
        """Get all changes for a specific vertex."""
        return self._vertex_changes.get(vertex_id, [])

    def get_most_modified_vertices(self, top_n: int = 5) -> list[tuple[Any, int]]:
        """Get vertices with most modifications."""
        vertex_counts = {
            vid: len(changes) for vid, changes in self._vertex_changes.items()
        }
        return sorted(vertex_counts.items(), key=lambda x: x[1], reverse=True)[:top_n]

    def total_changes(self) -> int:
        """Get total number of changes."""
        return sum(self._event_counts.values())

    def __repr__(self) -> str:
        """String representation."""
        return f"ChangeTracker(total_changes={self.total_changes()})"
