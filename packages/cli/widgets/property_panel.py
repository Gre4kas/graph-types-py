# packages/cli/widgets/property_panel.py
from __future__ import annotations

from typing import Any, TYPE_CHECKING

from textual.widgets import Static

if TYPE_CHECKING:
    from packages.core.base_graph import BaseGraph


class PropertyPanel(Static):
    """Панель свойств текущего графа."""

    DEFAULT_CSS = """
    PropertyPanel {
        border: round magenta;
        width: 24;
    }
    """

    def update_from_graph(self, graph: BaseGraph) -> None:
        v = graph.vertex_count()
        e = graph.edge_count()
        directed = graph._directed
        repr_name = graph._representation.__class__.__name__

        # Оценка плотности
        if v <= 1:
            density = 0.0
        else:
            if directed:
                max_e = v * (v - 1)
            else:
                max_e = v * (v - 1) / 2
            density = e / max_e if max_e > 0 else 0.0

        info = [
            f"Type: {graph.__class__.__name__}",
            f"Directed: {directed}",
            f"Representation:",
            f"  {repr_name}",
            "",
            f"Vertices: {v}",
            f"Edges:    {e}",
            f"Density:  {density:.4f}",
        ]
        self.update("\n".join(info))
