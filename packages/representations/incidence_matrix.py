"""
Incidence matrix representation for hypergraphs.

This module provides utilities to convert hypergraphs to incidence matrix representation.
Rows represent vertices, columns represent hyperedges.
M[v, e] = 1 if vertex v is contained in hyperedge e.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import numpy as np

if TYPE_CHECKING:
    from packages.graphs.hypergraph import Hypergraph


def to_incidence_matrix(graph: Hypergraph) -> np.ndarray:
    """
    Convert hypergraph to incidence matrix.

    Args:
        graph: Source hypergraph

    Returns:
        NumPy 2D array where rows are vertices and columns are hyperedges
        
    Raises:
        TypeError: If graph is not a Hypergraph
    """
    from packages.graphs.hypergraph import Hypergraph as HypergraphClass

    if not isinstance(graph, HypergraphClass):
        msg = f"Expected Hypergraph, got {type(graph).__name__}"
        raise TypeError(msg)

    vertices = list(graph.vertices())
    hyperedges = list(graph.edges())
    
    n_vertices = len(vertices)
    n_edges = len(hyperedges)
    
    # Create vertex index mapping
    vertex_to_idx = {v.id: i for i, v in enumerate(vertices)}
    
    # Initialize matrix
    matrix = np.zeros((n_vertices, n_edges), dtype=np.int8)
    
    # Fill matrix
    for j, hyperedge in enumerate(hyperedges):
        for vertex_id in hyperedge.vertices:
            if vertex_id in vertex_to_idx:
                i = vertex_to_idx[vertex_id]
                matrix[i, j] = 1
                
    return matrix
