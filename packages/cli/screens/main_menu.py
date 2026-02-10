"""
Main menu screen for graph type selection.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from textual.app import ComposeResult
from textual.containers import Container, Vertical
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Label, Static

if TYPE_CHECKING:
    from textual.app import App


class MainMenuScreen(Screen[None]):
    """
    Main menu for selecting graph type or loading existing graph.

    Options:
    - Create Simple Graph
    - Create Multigraph
    - Create Pseudograph
    - Create Hypergraph
    - Load from file
    - Recent files
    """

    BINDINGS = [
        ("1", "create_simple", "Simple Graph"),
        ("2", "create_multi", "Multigraph"),
        ("3", "create_pseudo", "Pseudograph"),
        ("4", "create_hyper", "Hypergraph"),
        ("l", "load_file", "Load File"),
        ("q", "quit", "Quit"),
    ]

    def compose(self) -> ComposeResult:
        """Compose main menu UI."""
        yield Header()
        yield Container(
            Vertical(
                Label("Welcome to Graph Library TUI", id="title"),
                Label("Select graph type to create:", id="subtitle"),
                Button("1. Simple Graph", id="btn_simple", variant="primary"),
                Button("2. Multigraph", id="btn_multi", variant="primary"),
                Button("3. Pseudograph", id="btn_pseudo", variant="primary"),
                Button("4. Hypergraph", id="btn_hyper", variant="primary"),
                Button("Load from file", id="btn_load", variant="success"),
                Static("", id="recent_files"),
                id="menu_container",
            ),
            id="main_container",
        )
        yield Footer()

    def on_mount(self) -> None:
        """Load recent files on mount."""
        self._load_recent_files()

    def _load_recent_files(self) -> None:
        """Load and display recent files."""
        recent_widget = self.query_one("#recent_files", Static)
        
        # Check for recent files
        recent_dir = Path.home() / ".graph-tui" / "recent"
        if recent_dir.exists():
            recent_files = sorted(
                recent_dir.glob("*.json"),
                key=lambda p: p.stat().st_mtime,
                reverse=True,
            )[:5]
            
            if recent_files:
                lines = ["", "Recent files:"]
                for i, file in enumerate(recent_files, 1):
                    lines.append(f"  {i}. {file.name}")
                recent_widget.update("\n".join(lines))

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        button_id = event.button.id

        if button_id == "btn_simple":
            self.action_create_simple()
        elif button_id == "btn_multi":
            self.action_create_multi()
        elif button_id == "btn_pseudo":
            self.action_create_pseudo()
        elif button_id == "btn_hyper":
            self.action_create_hyper()
        elif button_id == "btn_load":
            self.action_load_file()

    def action_create_simple(self) -> None:
        """Create Simple Graph."""
        from packages.cli.screens.representation_selector import (
            RepresentationSelectorScreen,
        )

        self.app.push_screen(
            RepresentationSelectorScreen(graph_type="simple"),
        )

    def action_create_multi(self) -> None:
        """Create Multigraph."""
        from packages.cli.screens.representation_selector import (
            RepresentationSelectorScreen,
        )

        self.app.push_screen(
            RepresentationSelectorScreen(graph_type="multi"),
        )

    def action_create_pseudo(self) -> None:
        """Create Pseudograph."""
        from packages.cli.screens.representation_selector import (
            RepresentationSelectorScreen,
        )

        self.app.push_screen(
            RepresentationSelectorScreen(graph_type="pseudo"),
        )

    def action_create_hyper(self) -> None:
        """Create Hypergraph."""
        from packages.cli.screens.representation_selector import (
            RepresentationSelectorScreen,
        )

        self.app.push_screen(
            RepresentationSelectorScreen(graph_type="hyper"),
        )

    def action_load_file(self) -> None:
        """Load graph from file."""
        from packages.cli.screens.import_export import ImportScreen

        self.app.push_screen(ImportScreen())
