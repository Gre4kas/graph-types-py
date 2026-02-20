# packages/cli/screens/import_export.py
from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ValidationError
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Input, Label, Select, TextArea, ProgressBar

from packages.utils.serializers import JSONSerializer
from packages.integrations.networkx_adapter import NetworkXAdapter
from packages.graphs.factory import GraphFactory


class ImportPreviewModel(BaseModel):
    """Pydantic-модель для базовой валидации JSON-графа."""

    graph_type: str
    directed: bool
    vertices: list[dict[str, Any]]
    edges: list[dict[str, Any]]


class ImportExportScreen(Screen[None]):
    """Экран импорта графа из файла."""

    BINDINGS = [("escape", "back", "Back")]

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(id="import-root"):
            with Horizontal():
                yield Select(
                    options=[
                        ("JSON (native)", "json"),
                        ("GraphML (NetworkX)", "graphml"),
                        ("Graphviz DOT", "dot"),
                        ("CSV Edge List", "csv"),
                    ],
                    id="format",
                    prompt="Формат",
                )
                yield Input(placeholder="Путь к файлу", id="path")
                yield Button("Загрузить", id="btn-load", variant="primary")

            yield TextArea(
                placeholder="Preview (первые 10 строк)",
                id="preview",
                height=10,
                read_only=True,
            )
            yield ProgressBar(total=100, id="progress")

        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-load":
            asyncio.create_task(self._load_async())

    def action_back(self) -> None:
        self.app.pop_screen()

    async def _load_async(self) -> None:
        fmt = self.query_one("#format", Select).value
        path_str = self.query_one("#path", Input).value.strip()
        if not path_str:
            return
        path = Path(path_str)

        preview = self.query_one("#preview", TextArea)
        bar = self.query_one("#progress", ProgressBar)

        if not path.exists():
            preview.text = "Файл не найден"
            return

        # Preview
        def _read_preview() -> str:
            text = path.read_text(encoding="utf-8", errors="ignore")
            return "\n".join(text.splitlines()[:10])

        preview.text = await asyncio.to_thread(_read_preview)

        bar.update(total=100, progress=10)

        # Импорт
        if fmt == "json":
            graph = await asyncio.to_thread(JSONSerializer.load, path)
        else:
            # через NetworkXAdapter/GraphConverter
            import networkx as nx

            def _read_nx() -> Any:
                if fmt == "graphml":
                    g = nx.read_graphml(path)
                elif fmt == "dot":
                    g = nx.nx_pydot.read_dot(path)
                elif fmt == "csv":
                    g = nx.read_edgelist(path, delimiter=",")
                else:
                    raise ValueError("unknown format")
                return g

            nx_graph = await asyncio.to_thread(_read_nx)
            graph = NetworkXAdapter.from_networkx(nx_graph)

        bar.update(progress=100)

        # Переход в редактор
        from packages.cli.screens.graph_editor import GraphEditorScreen

        self.app.pop_screen()
        self.app.push_screen(GraphEditorScreen(graph))
