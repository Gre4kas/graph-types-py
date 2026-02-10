"""
Edge model with Pydantic validation.

This module defines the Edge class which represents a connection between
vertices in a graph with optional weight and arbitrary attributes.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field, field_validator

if TYPE_CHECKING:
    from packages.core.vertex import Vertex

# Generic type for vertex identifiers
VertexId = TypeVar("VertexId", bound=str | int)


class Edge(BaseModel, Generic[VertexId]):
    """
    Represents an edge (connection) between two vertices in a graph.

    This class uses Pydantic v2 for automatic validation of edge data,
    including weight validation and attribute type checking.

    Attributes:
        source: Source vertex identifier
        target: Target vertex identifier
        weight: Edge weight (default: 1.0)
        directed: Whether this edge is directed (default: False)
        attributes: Arbitrary key-value pairs for edge metadata
        _hash_cache: Cached hash value for performance

    Type Parameters:
        VertexId: Type of vertex identifier

    Examples:
        >>> edge = Edge(source="A", target="B", weight=5.0)
        >>> edge.source
        'A'
        >>> edge.weight
        5.0
        >>> edge.is_self_loop()
        False

    Notes:
        - Edges are immutable by default (frozen=True)
        - Hash considers direction for directed edges
        - Weight must be non-negative (validated)
    """

    model_config = ConfigDict(
        frozen=True,
        validate_assignment=True,
        arbitrary_types_allowed=True,
    )

    __slots__ = ("_hash_cache",)

    source: VertexId = Field(..., description="Source vertex identifier")
    target: VertexId = Field(..., description="Target vertex identifier")
    weight: float = Field(default=1.0, ge=0.0, description="Edge weight (non-negative)")
    directed: bool = Field(default=False, description="Whether edge is directed")
    attributes: dict[str, Any] = Field(
        default_factory=dict,
        description="Arbitrary metadata for the edge",
    )

    @field_validator("weight")
    @classmethod
    def validate_weight(cls, v: float) -> float:
        """
        Validate edge weight is non-negative.

        Args:
            v: Weight value to validate

        Returns:
            Validated weight

        Raises:
            ValueError: If weight is negative or NaN
        """
        import math

        if math.isnan(v):
            msg = "Edge weight cannot be NaN"
            raise ValueError(msg)
        if v < 0:
            msg = f"Edge weight must be non-negative, got {v}"
            raise ValueError(msg)
        return v

    def is_self_loop(self) -> bool:
        """Check if this edge is a self-loop (source == target)."""
        return self.source == self.target

    def get_attribute(self, key: str, default: Any = None) -> Any:
        """
        Safely get an edge attribute with default value.

        Args:
            key: Attribute key
            default: Value to return if key doesn't exist

        Returns:
            Attribute value or default
        """
        return self.attributes.get(key, default)

    def __getitem__(self, key: str) -> Any:
        """
        Allow dictionary-like access to fields and attributes.
        
        Prioritizes fields (source, target, weight, directed),
        then looks in attributes.
        """
        if hasattr(self, key) and key in self.model_fields:
            return getattr(self, key)
        if key in self.attributes:
            return self.attributes[key]
        raise KeyError(f"Key {key!r} not found in Edge fields or attributes")

    def reverse(self) -> Edge[VertexId]:
        """
        Create a reversed edge (target -> source).

        Returns:
            New Edge with source and target swapped

        Examples:
            >>> edge = Edge(source="A", target="B", weight=5.0)
            >>> reversed_edge = edge.reverse()
            >>> reversed_edge.source
            'B'
        """
        return Edge(
            source=self.target,
            target=self.source,
            weight=self.weight,
            directed=self.directed,
            attributes=self.attributes.copy(),
        )

    def __hash__(self) -> int:
        """
        Hash based on source, target, and direction.

        For undirected edges, hash is symmetric (A-B == B-A).
        For directed edges, hash considers direction (A->B != B->A).

        Returns:
            Hash value of the edge
        """
        if not hasattr(self, "_hash_cache"):
            if self.directed:
                hash_value = hash((self.source, self.target, True))
            else:
                # Symmetric hash for undirected edges
                hash_value = hash(frozenset([self.source, self.target]))
            object.__setattr__(self, "_hash_cache", hash_value)
        return self._hash_cache

    def __eq__(self, other: object) -> bool:
        """
        Equality based on source, target, and direction.

        For undirected edges, (A, B) == (B, A).
        For directed edges, (A, B) != (B, A).

        Args:
            other: Object to compare with

        Returns:
            True if edges are equal
        """
        if not isinstance(other, Edge):
            return NotImplemented

        if self.directed != other.directed:
            return False

        if self.directed:
            return self.source == other.source and self.target == other.target

        # Undirected: check both orientations
        return (self.source == other.source and self.target == other.target) or (
            self.source == other.target and self.target == other.source
        )

    def __repr__(self) -> str:
        """Concise string representation."""
        arrow = "->" if self.directed else "--"
        weight_str = f", weight={self.weight}" if self.weight != 1.0 else ""
        return f"Edge({self.source!r} {arrow} {self.target!r}{weight_str})"

    def __str__(self) -> str:
        """Human-readable string representation."""
        arrow = "→" if self.directed else "↔"
        if self.weight != 1.0:
            return f"{self.source} {arrow} {self.target} (w={self.weight})"
        return f"{self.source} {arrow} {self.target}"
