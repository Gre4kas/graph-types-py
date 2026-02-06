"""Integration adapters for external libraries."""

from packages.integrations.networkx_adapter import (
    NETWORKX_AVAILABLE,
    NetworkXAdapter,
    NetworkXAlgorithms,
    requires_networkx,
)

try:
    from packages.integrations.graph_tool_adapter import (
        GRAPH_TOOL_AVAILABLE,
        GraphToolAdapter,
        GraphToolVisualizer,
        requires_graph_tool,
    )
except ImportError:
    GRAPH_TOOL_AVAILABLE = False
    GraphToolAdapter = None
    GraphToolVisualizer = None
    requires_graph_tool = None

__all__ = [
    "NetworkXAdapter",
    "NetworkXAlgorithms",
    "NETWORKX_AVAILABLE",
    "requires_networkx",
    "GraphToolAdapter",
    "GraphToolVisualizer",
    "GRAPH_TOOL_AVAILABLE",
    "requires_graph_tool",
]
