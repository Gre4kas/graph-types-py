"""
Custom exceptions for graph library.

This module defines a hierarchy of exceptions for different error conditions,
following Python best practices for exception design.
"""

from __future__ import annotations


class GraphError(Exception):
    """Base exception for all graph-related errors."""


class VertexNotFoundError(GraphError, KeyError):
    """Raised when attempting to access a non-existent vertex."""


class EdgeNotFoundError(GraphError, KeyError):
    """Raised when attempting to access a non-existent edge."""


class GraphConstraintError(GraphError, ValueError):
    """
    Raised when an operation violates graph-specific constraints.

    Examples:
    - Adding self-loop to simple graph
    - Adding multiple edges to non-multigraph
    - Invalid hyperedge in hypergraph
    """


class RepresentationError(GraphError):
    """Raised when representation conversion fails."""


class AlgorithmError(GraphError):
    """Raised when graph algorithm encounters invalid input or state."""


class ValidationError(GraphError, ValueError):
    """Raised when vertex/edge attribute validation fails."""
