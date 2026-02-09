# packages/cli/widgets/context_menu.py
from __future__ import annotations

from typing import Callable

from textual.app import ComposeResult
from textual.containers import Grid, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Label

class ContextMenuModal(ModalScreen[str]):
    """
    Modal screen for quick actions.
    Returns the action string when a button is pressed.
    """

    CSS = """
    ContextMenuModal {
        align: center middle;
    }

    #context-menu-container {
        width: 40;
        height: auto;
        border: thick $primary;
        background: $surface;
        padding: 1 2;
    }

    #context-menu-container > Label {
        text-align: center;
        width: 100%;
        margin-bottom: 1;
        text-style: bold;
    }

    #context-menu-container > Button {
        width: 100%;
        margin-bottom: 1; 
    }
    """

    def __init__(self, title: str = "Actions") -> None:
        super().__init__()
        self.menu_title = title

    def compose(self) -> ComposeResult:
        with Vertical(id="context-menu-container"):
            yield Label(self.menu_title)
            yield Button("Add Vertex (A)", id="add_vertex", variant="primary")
            yield Button("Add Edge (E)", id="add_edge", variant="primary")
            yield Button("Rename Vertex (F2)", id="rename_vertex")
            yield Button("Delete Selected (Del)", id="delete_selected", variant="error")
            yield Button("Cancel (Esc)", id="cancel")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        action = event.button.id
        if action == "cancel":
            self.dismiss(None)
        else:
            self.dismiss(action)
