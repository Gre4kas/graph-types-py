"""
Vertex model with Pydantic validation.

This module defines the Vertex class which represents a node in a graph
with arbitrary attributes validated through Pydantic v2.
"""

from __future__ import annotations

from typing import Any, Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field, field_validator

# Generic type for vertex identifier
VertexId = TypeVar("VertexId", bound=str | int)


class Vertex(BaseModel, Generic[VertexId]):
    """
    Represents a vertex (node) in a graph with validated attributes.

    This class uses Pydantic v2 for automatic validation of vertex data,
    ensuring data integrity and type safety.

    Attributes:
        id: Unique identifier for the vertex (immutable after creation)
        attributes: Arbitrary key-value pairs for vertex metadata
        _hash_cache: Cached hash value for performance (slots optimization)

    Type Parameters:
        VertexId: Type of vertex identifier (str, int, or hashable type)

    Examples:
        >>> vertex = Vertex(id="A", attributes={"color": "red", "weight": 42})
        >>> vertex.id
        'A'
        >>> vertex.attributes["color"]
        'red'
        >>> vertex.get_attribute("weight", default=0)
        42

    Notes:
        - Vertices are immutable by default (frozen=True in Pydantic v2)
        - Hash is based on id only for O(1) set/dict operations
        - Uses __slots__ for memory efficiency
    """

    model_config = ConfigDict(
        frozen=True,  # Immutable after creation
        str_strip_whitespace=True,  # Strip whitespace from string fields
        validate_assignment=True,  # Validate on attribute assignment
        arbitrary_types_allowed=True,  # Allow custom types in attributes
    )

    __slots__ = ("_hash_cache",)

    id: VertexId = Field(..., description="Unique identifier for the vertex")
    attributes: dict[str, Any] = Field(
        default_factory=dict,
        description="Arbitrary metadata for the vertex",
    )

    @field_validator("id")
    @classmethod
    def validate_id(cls, v: VertexId) -> VertexId:
        """
        Validate vertex identifier.

        Args:
            v: Vertex ID to validate

        Returns:
            Validated vertex ID

        Raises:
            ValueError: If ID is empty string or invalid
        """
        if isinstance(v, str) and not v.strip():
            msg = "Vertex ID cannot be empty string"
            raise ValueError(msg)
        return v

    def get_attribute(self, key: str, default: Any = None) -> Any:
        """
        Safely get a vertex attribute with default value.

        Args:
            key: Attribute key
            default: Value to return if key doesn't exist

        Returns:
            Attribute value or default
        """
        return self.attributes.get(key, default)

    def has_attribute(self, key: str) -> bool:
        """Check if vertex has a specific attribute."""
        return key in self.attributes

    def __hash__(self) -> int:
        """
        Hash based on vertex ID only.

        Cached for performance with repeated set/dict operations.

        Returns:
            Hash value of vertex ID
        """
        if not hasattr(self, "_hash_cache"):
            object.__setattr__(self, "_hash_cache", hash(self.id))
        return self._hash_cache

    def __eq__(self, other: object) -> bool:
        """
        Equality based on vertex ID only.

        Two vertices are equal if they have the same ID,
        regardless of attributes.

        Args:
            other: Object to compare with

        Returns:
            True if IDs match, False otherwise
        """
        if not isinstance(other, Vertex):
            return NotImplemented
        return self.id == other.id

    def __lt__(self, other: Vertex[VertexId]) -> bool:
        """
        Less-than comparison for sorting.

        Args:
            other: Vertex to compare with

        Returns:
            True if this vertex's ID is less than other's

        Raises:
            TypeError: If IDs are not comparable
        """
        if not isinstance(other, Vertex):
            return NotImplemented
        return self.id < other.id

    def __repr__(self) -> str:
        """Concise string representation."""
        attrs_str = f", {len(self.attributes)} attrs" if self.attributes else ""
        return f"Vertex({self.id!r}{attrs_str})"

    def __str__(self) -> str:
        """Human-readable string representation."""
        if self.attributes:
            attrs_preview = ", ".join(f"{k}={v!r}" for k, v in list(self.attributes.items())[:3])
            if len(self.attributes) > 3:
                attrs_preview += ", ..."
            return f"Vertex({self.id!r}, {{{attrs_preview}}})"
        return f"Vertex({self.id!r})"
