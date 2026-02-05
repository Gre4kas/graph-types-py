"""
Observer pattern implementation for graph changes.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class GraphObserver(ABC):
    """
    Abstract observer for graph change notifications.

    Examples:
        >>> class MyObserver(GraphObserver):
        ...     def update(self, event: str, *args):
        ...         print(f"Event: {event}, Args: {args}")
        >>> 
        >>> graph = SimpleGraph()
        >>> graph.attach_observer(MyObserver())
        >>> graph.add_vertex("A")  # Triggers notification
    """

    @abstractmethod
    def update(self, event: str, *args: Any, **kwargs: Any) -> None:
        """
        Called when graph changes.

        Args:
            event: Type of change ("vertex_added", "edge_removed", etc.)
            *args: Event-specific arguments
            **kwargs: Event-specific keyword arguments
        """
        ...


class ChangeLogger(GraphObserver):
    """
    Observer that logs all graph changes.

    Examples:
        >>> logger = ChangeLogger()
        >>> graph.attach_observer(logger)
        >>> graph.add_vertex("A")
        >>> logger.get_history()
        [('vertex_added', ('A',))]
    """

    def __init__(self) -> None:
        """Initialize change logger."""
        self._history: list[tuple[str, tuple[Any, ...]]] = []

    def update(self, event: str, *args: Any, **kwargs: Any) -> None:
        """Log the change."""
        self._history.append((event, args))

    def get_history(self) -> list[tuple[str, tuple[Any, ...]]]:
        """Get change history."""
        return self._history.copy()

    def clear_history(self) -> None:
        """Clear change history."""
        self._history.clear()

    def __repr__(self) -> str:
        """String representation."""
        return f"ChangeLogger(events={len(self._history)})"
