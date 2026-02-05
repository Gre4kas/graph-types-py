"""
Core abstractions for the Graph Library.
"""

__version__ = "0.1.0"

from packages.core.base_graph import BaseGraph
from packages.core.vertex import Vertex
from packages.core.edge import Edge

__all__ = [
    "BaseGraph",
    "Vertex",
    "Edge",
]
