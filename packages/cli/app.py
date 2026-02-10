"""
Main Textual application entry point.
"""

from __future__ import annotations

import sys
from pathlib import Path

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.driver import Driver

# Removed sys.path manipulation to avoid RuntimeWarning when running with -m

from packages.cli.screens.main_menu import MainMenuScreen


class GraphTUIApp(App[None]):
    """
    Interactive Terminal UI for Graph Library.

    Features:
    - Full CRUD operations for all graph types
    - Dynamic representation switching
    - Algorithm visualization
    - Import/Export in multiple formats
    - Real-time observer pattern monitoring

    Keyboard Shortcuts:
        Ctrl+Q: Quit application
        Ctrl+M: Return to main menu
        F1: Help
    """

    CSS_PATH = "styles.tcss"
    TITLE = "Graph Library TUI"
    SUB_TITLE = "Interactive Graph Manipulation"

    BINDINGS = [
        Binding("ctrl+q", "quit", "Quit", show=True, priority=True),
        Binding("ctrl+m", "main_menu", "Main Menu", show=True),
        Binding("f1", "help", "Help", show=True),
    ]

    def on_mount(self) -> None:
        """Show main menu on startup."""
        self.push_screen(MainMenuScreen())

    def action_main_menu(self) -> None:
        """Return to main menu."""
        # Pop all screens and push main menu
        while len(self.screen_stack) > 1:
            self.pop_screen()
        self.push_screen(MainMenuScreen())

    def action_help(self) -> None:
        """Show help screen."""
        from packages.cli.screens.help_screen import HelpScreen

        self.push_screen(HelpScreen())


def main() -> None:
    """Application entry point."""
    app = GraphTUIApp()
    app.run()


if __name__ == "__main__":
    main()
