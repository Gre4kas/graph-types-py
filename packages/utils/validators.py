"""
Validators for graph attributes and operations.

This module provides Pydantic validators and utility functions for
ensuring data integrity across the graph library.
"""

from __future__ import annotations

import math
from typing import Any

from pydantic import field_validator


def validate_weight(weight: float) -> float:
    """
    Validate edge weight is non-negative and not NaN.

    Args:
        weight: Weight value to validate

    Returns:
        Validated weight

    Raises:
        ValueError: If weight is negative or NaN
    """
    if math.isnan(weight):
        msg = "Edge weight cannot be NaN"
        raise ValueError(msg)
    if weight < 0:
        msg = f"Edge weight must be non-negative, got {weight}"
        raise ValueError(msg)
    return weight


def validate_vertex_id(vertex_id: Any) -> Any:
    """
    Validate vertex identifier is hashable and non-empty.

    Args:
        vertex_id: Vertex ID to validate

    Returns:
        Validated vertex ID

    Raises:
        TypeError: If vertex ID is not hashable
        ValueError: If vertex ID is empty string
    """
    # Check hashable
    try:
        hash(vertex_id)
    except TypeError as e:
        msg = f"Vertex ID must be hashable, got {type(vertex_id).__name__}"
        raise TypeError(msg) from e

    # Check non-empty string
    if isinstance(vertex_id, str) and not vertex_id.strip():
        msg = "Vertex ID cannot be empty string"
        raise ValueError(msg)

    return vertex_id


def validate_hyperedge_vertices(vertices: set[Any]) -> set[Any]:
    """
    Validate hyperedge contains at least 2 vertices.

    Args:
        vertices: Set of vertex identifiers

    Returns:
        Validated vertex set

    Raises:
        ValueError: If hyperedge has less than 2 vertices
    """
    if len(vertices) < 2:
        msg = f"Hyperedge must contain at least 2 vertices, got {len(vertices)}"
        raise ValueError(msg)
    return vertices
