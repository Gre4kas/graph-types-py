"""
Screen for selecting graph representation.
"""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Container, Vertical
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Label, RadioButton, RadioSet


class RepresentationSelectorScreen(Screen[None]):
    """
    Modal screen for selecting graph representation.

    Representations:
    - Adjacency List (recommended for sparse graphs)
    - Adjacency Matrix (recommended for dense graphs)
    - Edge List (universal, good for serialization)
    """

    def __init__(self, graph_type: str, directed: bool = False) -> None:
        """
        Initialize representation selector.

        Args:
            graph_type: Type of graph (simple, multi, pseudo, hyper)
            directed: Whether graph is directed
        """
        super().__init__()
        self.graph_type = graph_type
        self.directed = directed

    def compose(self) -> ComposeResult:
        """Compose representation selector UI."""
        yield Header()
        yield Container(
            Vertical(
                Label(f"Select representation for {self.graph_type} graph", id="title"),
                Label("", id="subtitle"),
                RadioSet(
                    RadioButton("Adjacency List (recommended)", value=True, id="radio_list"),
                    RadioButton("Adjacency Matrix", id="radio_matrix"),
                    RadioButton("Edge List", id="radio_edge"),
                    id="radio_set",
                ),
                Label("", id="description"),
                Container(
                    Button("Create", variant="primary", id="btn_create"),
                    Button("Cancel", variant="default", id="btn_cancel"),
                    id="button_container",
                ),
                id="selector_container",
            ),
            id="main_container",
        )
        yield Footer()

    def on_mount(self) -> None:
        """Update descriptions on mount."""
        self._update_description("adjacency_list")

    def on_radio_set_changed(self, event: RadioSet.Changed) -> None:
        """Update description when selection changes."""
        selected = event.pressed
        if selected.id == "radio_list":
            self._update_description("adjacency_list")
        elif selected.id == "radio_matrix":
            self._update_description("adjacency_matrix")
        elif selected.id == "radio_edge":
            self._update_description("edge_list")

    def _update_description(self, repr_type: str) -> None:
        """Update description text."""
        desc_widget = self.query_one("#description", Label)
        
        descriptions = {
            "adjacency_list": (
                "✓ O(V + E) memory\n"
                "✓ Fast neighbor iteration\n"
                "✓ Good for sparse graphs\n"
                "- Slow edge existence check"
            ),
            "adjacency_matrix": (
                "✓ O(1) edge existence check\n"
                "✓ Good for dense graphs\n"
                "- O(V²) memory\n"
                "⚠ Slow for |V| > 1000"
            ),
            "edge_list": (
                "✓ Universal format\n"
                "✓ Easy serialization\n"
                "✓ Minimal memory\n"
                "- Slow queries"
            ),
        }
        
        desc_widget.update(descriptions.get(repr_type, ""))

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "btn_cancel":
            self.app.pop_screen()
        elif event.button.id == "btn_create":
            self._create_graph()

    def _create_graph(self) -> None:
        """Create graph with selected representation."""
        from packages.cli.screens.graph_editor import GraphEditorScreen
        from packages.graphs.factory import GraphFactory

        # Get selected representation
        radio_set = self.query_one("#radio_set", RadioSet)
        selected = radio_set.pressed_button
        
        if selected.id == "radio_list":
            repr_type = "adjacency_list"
        elif selected.id == "radio_matrix":
            repr_type = "adjacency_matrix"
        else:
            repr_type = "edge_list"

        # Create graph using factory
        graph = GraphFactory.create_graph(
            graph_type=self.graph_type,
            directed=self.directed,
            representation=repr_type,
        )

        # Navigate to graph editor
        self.app.pop_screen()  # Remove selector
        self.app.push_screen(GraphEditorScreen(graph))
