"""
Observer pattern implementation for graph changes.

This module provides the abstract base class for observers that want
to be notified of graph modifications.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class GraphObserver(ABC):
    """
    Abstract observer for graph change notifications.

    Observers implementing this interface can be attached to graphs
    to receive notifications when vertices or edges are added/removed.

    Examples:
        >>> class PrintObserver(GraphObserver):
        ...     def update(self, event: str, *args, **kwargs):
        ...         print(f"Graph changed: {event} with {args}")
        >>> 
        >>> graph = SimpleGraph()
        >>> observer = PrintObserver()
        >>> graph.attach_observer(observer)
        >>> graph.add_vertex("A")  # Prints: Graph changed: vertex_added with ('A',)
    """

    @abstractmethod
    def update(self, event: str, *args: Any, **kwargs: Any) -> None:
        """
        Called when graph changes occur.

        Args:
            event: Type of change event. Common events:
                - "vertex_added": args = (vertex_id,)
                - "vertex_removed": args = (vertex_id,)
                - "edge_added": args = (source, target)
                - "edge_removed": args = (source, target)
                - "representation_changed": args = (new_repr_type,)
            *args: Event-specific positional arguments
            **kwargs: Event-specific keyword arguments
        """
        ...


class ConsoleObserver(GraphObserver):
    """
    Simple observer that prints changes to console.

    Useful for debugging and development.

    Examples:
        >>> graph = SimpleGraph()
        >>> graph.attach_observer(ConsoleObserver())
        >>> graph.add_vertex("A")
        [GRAPH] vertex_added: A
    """

    def __init__(self, prefix: str = "[GRAPH]") -> None:
        """
        Initialize console observer.

        Args:
            prefix: Prefix for console messages
        """
        self.prefix = prefix

    def update(self, event: str, *args: Any, **kwargs: Any) -> None:
        """Print change to console."""
        args_str = ", ".join(str(arg) for arg in args)
        print(f"{self.prefix} {event}: {args_str}")
