# packages/cli/screens/algorithm_runner.py
from __future__ import annotations

from typing import Any, TYPE_CHECKING

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Button, Checkbox, Input, Label, Select, DataTable, Footer, Header

from packages.algorithms.traversal import bfs, dfs
from packages.algorithms.shortest_path import dijkstra, bellman_ford
from packages.algorithms.minimum_spanning_tree import prim_mst, kruskal_mst  # пример
from packages.integrations.networkx_adapter import NetworkXAlgorithms

if TYPE_CHECKING:
    from packages.core.base_graph import BaseGraph


class AlgorithmRunnerScreen(Screen[None]):
    """Экран запуска алгоритмов с опцией пошаговой визуализации."""

    BINDINGS = [
        ("escape", "back", "Back"),
    ]

    def __init__(self, graph: BaseGraph) -> None:
        super().__init__()
        self.graph = graph

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(id="algo-root"):
            with Horizontal():
                yield Select(
                    options=[
                        ("BFS", "bfs"),
                        ("DFS", "dfs"),
                        ("Dijkstra", "dijkstra"),
                        ("Bellman-Ford", "bellman_ford"),
                        ("Prim MST", "prim"),
                        ("Kruskal MST", "kruskal"),
                        ("PageRank", "pagerank"),
                    ],
                    id="algo-select",
                    prompt="Алгоритм",
                )
                yield Input(placeholder="Стартовая вершина", id="start-vertex")
                yield Checkbox(label="Пошаговая визуализация", id="step-by-step")
                yield Button("Запустить (Enter)", id="btn-run", variant="primary")

            yield DataTable(id="algo-result")

        yield Footer()

    def on_mount(self) -> None:
        self.query_one("#algo-result", DataTable).add_column("Vertex")
        self.query_one("#algo-result", DataTable).add_column("Value")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-run":
            self._run_algorithm()

    def action_back(self) -> None:
        self.app.pop_screen()

    def _run_algorithm(self) -> None:
        select = self.query_one("#algo-select", Select)
        algo = select.value
        start = self.query_one("#start-vertex", Input).value.strip() or None
        step = self.query_one("#step-by-step", Checkbox).value

        table = self.query_one("#algo-result", DataTable)
        table.clear()

        if algo in ("bfs", "dfs") and not start:
            return

        if algo == "bfs":
            order = BFSRunner(self.graph, start, step).run()
            table.add_row("Order", " -> ".join(map(str, order)))
        elif algo == "dfs":
            order = DFSRunner(self.graph, start, step).run()
            table.add_row("Order", " -> ".join(map(str, order)))
        elif algo == "dijkstra":
            dist = dijkstra(self.graph, start)
            for v, d in dist.items():
                table.add_row(str(v), str(d))
        elif algo == "bellman_ford":
            dist = bellman_ford(self.graph, start)
            for v, d in dist.items():
                table.add_row(str(v), str(d))
        elif algo == "prim":
            mst = prim_mst(self.graph)
            table.add_row("MST edges", str(list(mst.edges())))
        elif algo == "kruskal":
            mst = kruskal_mst(self.graph)
            table.add_row("MST edges", str(list(mst.edges())))
        elif algo == "pagerank":
            ranks = NetworkXAlgorithms.pagerank(self.graph)
            for v, r in ranks.items():
                table.add_row(str(v), f"{r:.4f}")


class BFSRunner:
    """Каркас для BFS с опциональной пошаговой визуализацией."""

    def __init__(
        self,
        graph: BaseGraph,
        start: Any,
        step_visual: bool,
    ) -> None:
        self.graph = graph
        self.start = start
        self.step_visual = step_visual

    def run(self) -> list[Any]:
        # можно использовать algorithms.traversal.bfs со своим callback
        order: list[Any] = []

        def _visit(v: Any) -> None:
            order.append(v)
            # TODO: интеграция с GraphCanvas для подсветки шага

        bfs(self.graph, self.start, visit=_visit)
        return order


class DFSRunner:
    def __init__(
        self,
        graph: BaseGraph,
        start: Any,
        step_visual: bool,
    ) -> None:
        self.graph = graph
        self.start = start
        self.step_visual = step_visual

    def run(self) -> list[Any]:
        order: list[Any] = []

        def _visit(v: Any) -> None:
            order.append(v)

        dfs(self.graph, self.start, visit=_visit)
        return order
