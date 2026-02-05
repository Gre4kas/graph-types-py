"""
Graph Library - Professional Python library for graph theory.

Supports all mathematical graph types: Simple, Multigraph, Pseudograph, Hypergraph.
"""

__version__ = "0.1.0"

from packages.graphs.simple_graph import SimpleGraph
from packages.graphs.multigraph import Multigraph
from packages.graphs.pseudograph import Pseudograph
from packages.graphs.hypergraph import Hypergraph

__all__ = [
    "SimpleGraph",
    "Multigraph",
    "Pseudograph",
    "Hypergraph",
]
