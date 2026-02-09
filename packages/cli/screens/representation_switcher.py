"""
Screen for selecting graph representation.
"""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Any, Callable

from textual.app import ComposeResult
from textual.containers import Vertical, Horizontal
from textual.screen import ModalScreen
from textual.widgets import Button, Label, RadioButton, RadioSet

from packages.converters.representation_converters import RepresentationConverter

if TYPE_CHECKING:
    from packages.core.base_graph import BaseGraph
    from packages.representations.base_representation import BaseRepresentation

# Fix: Move OnApplied inside TYPE_CHECKING or use Any
# Option 1: Use string annotation (forward reference)
OnApplied = Callable[["BaseRepresentation", "BaseRepresentation"], None]

# OR Option 2: Use Any (simpler, works immediately)
# OnApplied = Callable[[Any, Any], None]


class RepresentationSwitcherModal(ModalScreen[None]):
    """Modal screen for switching graph representation."""

    def __init__(
        self,
        graph: BaseGraph,
        on_applied: OnApplied,
    ) -> None:
        super().__init__()
        self._graph = graph
        self._on_applied = on_applied

    def compose(self) -> ComposeResult:
        """Compose representation switcher UI."""
        with Vertical(id="repr-switcher"):
            yield Label("Change graph representation", id="title")
            yield Label(
                "Adjacency Matrix for |V| > 1000 may be very slow.",
                id="warning",
            )
            yield RadioSet(
                RadioButton("Adjacency List", id="radio_list"),
                RadioButton("Adjacency Matrix", id="radio_matrix"),
                RadioButton("Edge List", id="radio_edge"),
                id="radio_set",
            )
            with Horizontal():
                yield Button("Apply", variant="primary", id="btn-apply")
                yield Button("Cancel", id="btn-cancel")

    def on_mount(self) -> None:
        """Select current representation on mount."""
        current = self._graph._representation.__class__.__name__.lower()
        rs = self.query_one("#radio_set", RadioSet)
        if "list" in current:
            rs.press_button("radio_list")
        elif "matrix" in current:
            rs.press_button("radio_matrix")
        else:
            rs.press_button("radio_edge")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "btn-cancel":
            self.app.pop_screen()
            return

        if event.button.id == "btn-apply":
            asyncio.create_task(self._apply_async())

    async def _apply_async(self) -> None:
        """Apply representation change asynchronously."""
        rs = self.query_one("#radio_set", RadioSet)
        selected = rs.pressed_button
        if selected.id == "radio_list":
            target = "adjacency_list"
        elif selected.id == "radio_matrix":
            target = "adjacency_matrix"
        else:
            target = "edge_list"

        # Heavy operation in separate thread
        def _convert() -> tuple[Any, Any]:
            old_repr = self._graph._representation
            # RepresentationConverter.convert returns a new graph instance
            new_graph = RepresentationConverter.convert(
                self._graph,
                target_representation=target,
            )
            new_repr = new_graph._representation
            
            # Update the original graph's representation
            self._graph._representation = new_repr
            
            return old_repr, new_repr

        old_repr, new_repr = await asyncio.to_thread(_convert)
        self._on_applied(old_repr, new_repr)
        self.app.pop_screen()
