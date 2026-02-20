# packages/cli/screens/algorithm_runner.py
from __future__ import annotations

from typing import Any, TYPE_CHECKING, Iterator

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Button, Checkbox, Input, Label, Select, DataTable, Footer, Header
from textual.timer import Timer

from packages.cli.widgets.graph_canvas import GraphCanvas
from packages.algorithms.traversal import bfs, dfs
from packages.algorithms.shortest_path import dijkstra, bellman_ford
from packages.algorithms.minimum_spanning_tree import prim_mst, kruskal_mst
from packages.integrations.networkx_adapter import NetworkXAlgorithms

if TYPE_CHECKING:
    from packages.core.base_graph import BaseGraph


class AlgorithmRunnerScreen(Screen[None]):
    """
    Screen for running algorithms with optional step-by-step visualization.
    """

    BINDINGS = [
        ("escape", "back", "Back"),
        ("space", "toggle_pause", "Pause/Resume"),
    ]

    CSS = """
    AlgorithmRunnerScreen {
        align: center middle;
    }
    
    #algo-controls {
        height: 3;
        dock: bottom;
        align: center middle;
        background: $primary-darken-1;
    }
    
    #canvas-container {
        width: 100%;
        height: 1fr;
        border: solid $success;
    }
    
    #results-container {
        width: 40%;
        height: 1fr;
    }
    """

    def __init__(self, graph: BaseGraph) -> None:
        super().__init__()
        self.graph = graph
        self._iterator: Iterator[Any] | None = None
        self._timer: Timer | None = None
        self._visited_order: list[Any] = []
        self._is_paused = False

    def compose(self) -> ComposeResult:
        yield Header()
        
        with Horizontal(id="algo-main"):
            # Left: Visualization Canvas
            yield GraphCanvas(id="algo-canvas")
            
            # Right: Controls & Results
            with Vertical(id="results-container"):
                yield Label("Algorithm Settings", classes="header")
                yield Select(
                    options=[
                        ("BFS", "bfs"),
                        ("DFS", "dfs"),
                        ("Dijkstra", "dijkstra"),
                    ],
                    id="algo-select",
                    value="bfs",
                    allow_blank=False,
                )
                yield Input(placeholder="Start Vertex ID", id="start-vertex")
                yield Checkbox("Step-by-step Visualization", value=True, id="step-by-step")
                yield Button("Run Algorithm", id="btn-run", variant="primary")
                
                yield Label("Results / Log", classes="header")
                yield DataTable(id="algo-result")

        yield Footer()

    def on_mount(self) -> None:
        # Init DataTable
        table = self.query_one("#algo-result", DataTable)
        table.add_column("Step")
        table.add_column("Event / Vertex")
        
        # Init Canvas
        canvas = self.query_one("#algo-canvas", GraphCanvas)
        canvas.set_graph(self.graph)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-run":
            self._start_algorithm()

    def action_back(self) -> None:
        self._stop_timer()
        self.app.pop_screen()
        
    def action_toggle_pause(self) -> None:
        if self._timer:
            if self._is_paused:
                self._timer.resume()
                self._is_paused = False
                self.notify("Resumed")
            else:
                self._timer.pause()
                self._is_paused = True
                self.notify("Paused")

    def _stop_timer(self) -> None:
        if self._timer:
            self._timer.stop()
            self._timer = None

    def _start_algorithm(self) -> None:
        self._stop_timer()
        self._visited_order.clear()
        
        # Reset UI
        table = self.query_one("#algo-result", DataTable)
        table.clear()
        canvas = self.query_one("#algo-canvas", GraphCanvas)
        canvas.set_highlighted(set())
        
        # Get params
        select = self.query_one("#algo-select", Select)
        algo = select.value
        start_raw = self.query_one("#start-vertex", Input).value.strip()
        step_mode = self.query_one("#step-by-step", Checkbox).value

        # Basic validation
        if not start_raw:
            self.notify("Please enter a start vertex", severity="error")
            return
            
        # Try to infer type of ID (int vs str) based on existing vertices
        # This is a bit hacky, ideally ID type should be strict
        start_id: Any = start_raw
        if not self.graph.has_vertex(start_id):
            try:
                start_id = int(start_raw)
            except ValueError:
                pass
        
        if not self.graph.has_vertex(start_id):
            self.notify(f"Vertex {start_id} not found", severity="error")
            return

        # Prepare iterator
        try:
            if algo == "bfs":
                self._iterator = bfs(self.graph, start_id)
            elif algo == "dfs":
                self._iterator = dfs(self.graph, start_id)
            elif algo == "dijkstra":
                # Dijkstra usually returns a dict, not iterator. 
                # We can mock an iterator or just run it instantly.
                dist = dijkstra(self.graph, start_id)
                self._display_static_results(algo, dist)
                return
            else:
                self.notify(f"Video visualization not supported for {algo}", severity="warning")
                return

            if step_mode:
                # Start timer
                self._timer = self.set_interval(0.8, self._next_step)
            else:
                # Run instantly
                results = list(self._iterator)
                self._display_static_results(algo, results)

        except Exception as e:
            self.notify(f"Error starting algorithm: {e}", severity="error")

    def _next_step(self) -> None:
        """Called by timer to advance one step."""
        if not self._iterator:
            self._stop_timer()
            return
            
        try:
            vertex = next(self._iterator)
            self._visited_order.append(vertex)
            
            # Update UI
            table = self.query_one("#algo-result", DataTable)
            step_num = len(self._visited_order)
            table.add_row(str(step_num), f"Visited {vertex}")
            table.scroll_end()
            
            # Highlight current
            canvas = self.query_one("#algo-canvas", GraphCanvas)
            # Accumulate highlights for traversed path or just current? 
            # Let's highlight all visited so far to show path
            canvas.set_highlighted(set(self._visited_order))
            
        except StopIteration:
            self._stop_timer()
            self.notify("Algorithm Finished")
            # Final highlight
            canvas = self.query_one("#algo-canvas", GraphCanvas)
            canvas.set_highlighted(set(self._visited_order))

    def _display_static_results(self, algo: str, results: Any) -> None:
        table = self.query_one("#algo-result", DataTable)
        if isinstance(results, list):
             table.add_row("Results", " -> ".join(map(str, results)))
        elif isinstance(results, dict):
            for k, v in results.items():
                table.add_row(str(k), str(v))
