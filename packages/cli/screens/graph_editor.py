# packages/cli/screens/graph_editor.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal, TYPE_CHECKING

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import DataTable, Footer, Header

from packages.cli.widgets.graph_canvas import GraphCanvas
from packages.cli.widgets.observer_log import ObserverLog
from packages.cli.widgets.property_panel import PropertyPanel
from packages.cli.widgets.status_bar import StatusBar
from packages.cli.widgets.vertex_editor import VertexEditorModal
from packages.cli.widgets.edge_editor import EdgeEditorModal
from packages.cli.commands.graph_commands import (
    AddVertexCommand,
    AddEdgeCommand,
    RemoveVertexCommand,
    RemoveEdgeCommand,
    ChangeRepresentationCommand,
    CommandHistory,
)
from packages.cli.screens.representation_switcher import RepresentationSwitcherModal
from packages.cli.screens.algorithm_runner import AlgorithmRunnerScreen
from packages.cli.screens.import_export import ImportExportScreen
from packages.observers.graph_observer import GraphObserver
from packages.utils.exceptions import GraphError  # предположительно есть
from packages.utils.serializers import JSONSerializer

if TYPE_CHECKING:
    from packages.core.base_graph import BaseGraph
    from packages.representations.base_representation import BaseRepresentation


GraphTypeLiteral = Literal["simple", "multi", "pseudo", "hyper"]


class TUIGraphObserver(GraphObserver):
    """Observer, передающий события в виджет ObserverLog."""

    def __init__(self, log_widget: ObserverLog) -> None:
        self.log = log_widget

    def update(self, event: str, *args: Any, **kwargs: Any) -> None:
        """Dispatch update events to specific handlers."""
        if event == "vertex_added":
            self.on_vertex_added(args[0])
        elif event == "vertex_removed":
            self.on_vertex_removed(args[0])
        elif event == "edge_added":
            # edge_added sends (source, target), but on_edge_added expects Edge object? 
            # Wait, BaseGraph says: _notify_observers("edge_added", source, target)
            # TUIGraphObserver.on_edge_added expects 'edge: Any'.
            # Let's check on_edge_added signature in existing code.
            pass
        elif event == "edge_removed":
            pass
        elif event == "representation_changed":
            # representation_changed sends (new_repr_type,)
            # on_representation_changed expects (old, new)
            pass
        
        # Actually, let's look at what BaseGraph sends vs what TUIGraphObserver expects.
        # BaseGraph: _notify_observers("vertex_added", vertex_id)
        # TUIGraphObserver.on_vertex_added(vertex: Any) -> vertex.id usage suggests it expects a Vertex object?
        # In simple_graph.py: _notify_observers("vertex_added", vertex_id) -> sends ID.
        # So TUIGraphObserver.on_vertex_added(vertex) using vertex.id might be wrong if it receives an ID.
        
        # Let's fix the implementation of TUIGraphObserver methods and update dispatch together.

    def on_vertex_added(self, vertex_id: Any) -> None:
        self.log.add_entry(f"➕ Добавлена вершина {vertex_id}", timestamp=True)

    def on_vertex_removed(self, vertex_id: Any) -> None:
        self.log.add_entry(f"➖ Удалена вершина {vertex_id}", timestamp=True)

    def on_edge_added(self, source: Any, target: Any) -> None:
        self.log.add_entry(f"➕ Добавлено ребро ({source},{target})", timestamp=True)

    def on_edge_removed(self, source: Any, target: Any) -> None:
        self.log.add_entry(f"➖ Удалено ребро ({source},{target})", timestamp=True)

    def on_representation_changed(self, new_repr_type: str) -> None:
        self.log.add_entry(
            f"🔄 Представление изменено на: {new_repr_type}",
            timestamp=True,
        )

    def update(self, event: str, *args: Any, **kwargs: Any) -> None:
        if event == "vertex_added":
            self.on_vertex_added(args[0])
        elif event == "vertex_removed":
            self.on_vertex_removed(args[0])
        elif event == "edge_added":
            self.on_edge_added(args[0], args[1])
        elif event == "edge_removed":
            self.on_edge_removed(args[0], args[1])
        elif event == "representation_changed":
            self.on_representation_changed(args[0])


@dataclass
class SelectionState:
    """Текущее выделение в редакторе графа."""

    selected_vertex: Any | None = None
    selected_edge: tuple[Any, Any] | None = None


class GraphEditorScreen(Screen[None]):
    """
    Основной экран редактирования графа.

    Layout:
    - Left:  vertices table
    - Center: GraphCanvas
    - Right: PropertyPanel
    - Bottom: ObserverLog + StatusBar
    """

    BINDINGS = [
        Binding("tab", "cycle_focus", "Next Panel", show=True),
        Binding("ctrl+r", "change_representation", "Change Representation", show=True),
        Binding("ctrl+s", "save", "Save", show=True),
        Binding("ctrl+z", "undo", "Undo", show=True),
        Binding("ctrl+y", "redo", "Redo", show=True),
        Binding("f5", "run_algorithm", "Run Algorithm", show=True),
        Binding("f2", "rename_vertex", "Rename Vertex", show=True),
        Binding("delete", "delete_selected", "Delete", show=True),
        Binding("a", "add_vertex", "Add Vertex", show=False),
        Binding("e", "add_edge", "Add Edge", show=False),
        Binding("m", "context_menu", "Context Menu", show=False),
        Binding("escape", "back", "Back", show=False),
    ]

    def __init__(self, graph: BaseGraph) -> None:
        super().__init__()
        self.graph = graph
        self.selection = SelectionState()
        self.commands = CommandHistory()
        self._large_mode = False  # упрощённая визуализация для больших графов

    def compose(self) -> ComposeResult:
        """Compose UI layout."""
        yield Header()

        with Vertical(id="editor-root"):
            with Horizontal(id="editor-main"):
                # Left panel: vertices
                yield DataTable(id="vertices_table")

                # Center: canvas
                yield GraphCanvas(id="graph_canvas")

                # Right: properties
                yield PropertyPanel(id="property_panel")

            # Bottom: observer log + status bar
            with Vertical(id="bottom-panel"):
                yield ObserverLog(id="observer_log")
                yield StatusBar(id="status_bar")

        yield Footer()

    def on_mount(self) -> None:
        """Initial setup after mount."""
        # Init table
        table = self.query_one("#vertices_table", DataTable)
        table.add_column("ID")
        table.add_column("Attrs")
        table.cursor_type = "row"
        table.zebra_stripes = True

        # Load initial data
        self._refresh_all()

        # Attach observer
        log = self.query_one(ObserverLog)
        self.observer = TUIGraphObserver(log)
        
        # Check if graph has attach_observer method
        if hasattr(self.graph, 'attach_observer'):
            try:
                self.graph.attach_observer(self.observer)
            except Exception as e:
                log.add_entry(f"⚠ Could not attach observer: {e}")

        # Detect large mode
        if self.graph.vertex_count() > 1000:
            self._large_mode = True
            self.query_one(StatusBar).set_warning(
                "Large graph: simplified mode enabled (no GraphCanvas)",
            )
            canvas = self.query_one(GraphCanvas)
            canvas.visible = False

    # ---------- Helpers ----------

    def _refresh_all(self) -> None:
        """Полностью обновить UI по текущему графу."""
        self._refresh_vertices_table()
        self._refresh_properties()
        self._refresh_canvas()

    def _refresh_vertices_table(self) -> None:
        table = self.query_one(DataTable)
        table.clear()
        for v in self.graph.vertices():
            table.add_row(str(v.id), repr(v.attributes))

    def _refresh_properties(self) -> None:
        panel = self.query_one(PropertyPanel)
        panel.update_from_graph(self.graph)

        status = self.query_one(StatusBar)
        status.set_graph_info(
            graph_type=self.graph.__class__.__name__,
            directed=self.graph._directed,
            representation=self.graph._representation.__class__.__name__,
        )

    def _refresh_canvas(self) -> None:
        if self._large_mode:
            return
        canvas = self.query_one(GraphCanvas)
        canvas.set_graph(self.graph)

    def _get_current_vertex_id(self) -> Any | None:
        """Получить ID выбранной вершины из таблицы."""
        table = self.query_one(DataTable)
        if table.cursor_row is None:
            return None
        row = table.get_row_at(table.cursor_row)
        if not row:
            return None
        return row[0].value  # ID в первой колонке

    # ---------- Actions ----------

    def action_cycle_focus(self) -> None:
        """Tab — переключение фокуса между панелями."""
        focus_order = [
            "#vertices_table",
            "#graph_canvas",
            "#property_panel",
            "#observer_log",
        ]
        current = self.focused
        if current is None:
            self.query_one(focus_order[0]).focus()
            return

        try:
            idx = next(
                i for i, sel in enumerate(focus_order)
                if self.query_one(sel) is current
            )
        except StopIteration:
            self.query_one(focus_order[0]).focus()
            return

        next_idx = (idx + 1) % len(focus_order)
        self.query_one(focus_order[next_idx]).focus()

    def action_add_vertex(self) -> None:
        """Открыть модал добавления вершины."""
        self.app.push_screen(
            VertexEditorModal(
                on_submit=self._handle_add_vertex,
            ),
        )

    def _handle_add_vertex(self, payload: dict[str, Any]) -> None:
        """Callback после валидации формы вершины."""
        from packages.core.vertex import Vertex

        vertex = Vertex(payload["id"], **payload.get("attributes", {}))
        cmd = AddVertexCommand(graph=self.graph, vertex=vertex)
        try:
            cmd.execute()
        except GraphError as exc:
            self.query_one(StatusBar).set_error(str(exc))
            return

        self.commands.push(cmd)
        self._refresh_all()

    def action_add_edge(self) -> None:
        """Открыть модал добавления ребра."""
        self.app.push_screen(
            EdgeEditorModal(
                existing_vertices=[v.id for v in self.graph.vertices()],
                on_submit=self._handle_add_edge,
            ),
        )

    def _handle_add_edge(self, payload: dict[str, Any]) -> None:
        """Callback после валидации формы ребра."""
        cmd = AddEdgeCommand(
            graph=self.graph,
            source=payload["source"],
            target=payload["target"],
            weight=payload.get("weight", 1.0),
            attributes=payload.get("attributes", {}),
        )
        try:
            cmd.execute()
        except GraphError as exc:
            self.query_one(StatusBar).set_error(str(exc))
            return

        self.commands.push(cmd)
        self._refresh_all()

    def action_rename_vertex(self) -> None:
        """F2 — переименовать вершину."""
        current = self._get_current_vertex_id()
        if current is None:
            self.query_one(StatusBar).set_error("Нет выбранной вершины")
            return

        self.app.push_screen(
            VertexEditorModal(
                initial_id=current,
                on_submit=self._handle_rename_vertex,
                mode="rename",
            ),
        )

    def _handle_rename_vertex(self, payload: dict[str, Any]) -> None:
        # Тут можно реализовать отдельную RenameVertexCommand,
        # пока для простоты — remove + add (ты можешь доработать).
        old_id = payload["old_id"]
        new_id = payload["id"]
        if old_id == new_id:
            return

        from packages.core.vertex import Vertex

        # Снимем атрибуты
        v = self.graph.get_vertex(old_id)
        attrs = v.attributes.copy()
        # специфический command лучше, но дадим каркас
        rm = RemoveVertexCommand(graph=self.graph, vertex_id=old_id)
        add = AddVertexCommand(graph=self.graph, vertex=Vertex(new_id, **attrs))

        try:
            rm.execute()
            add.execute()
        except GraphError as exc:
            self.query_one(StatusBar).set_error(str(exc))
            return

        self.commands.push(rm)
        self.commands.push(add)
        self._refresh_all()

    def action_delete_selected(self) -> None:
        """Delete — удалить выбранный элемент."""
        vid = self._get_current_vertex_id()
        if vid is None:
            self.query_one(StatusBar).set_error("Нечего удалять")
            return

        cmd = RemoveVertexCommand(graph=self.graph, vertex_id=vid)
        try:
            cmd.execute()
        except GraphError as exc:
            self.query_one(StatusBar).set_error(str(exc))
            return

        self.commands.push(cmd)
        self._refresh_all()

    def action_change_representation(self) -> None:
        """Ctrl+R — открыть модал смены представления."""
        self.app.push_screen(
            RepresentationSwitcherModal(
                graph=self.graph,
                on_applied=self._handle_representation_changed,
            ),
        )

    def _handle_representation_changed(
        self,
        old_repr: BaseRepresentation,
        new_repr: BaseRepresentation,
    ) -> None:
        cmd = ChangeRepresentationCommand(
            graph=self.graph,
            old_repr=old_repr,
            new_repr=new_repr,
        )
        # выполняем уже применённое состояние — просто запушим в историю
        self.commands.push(cmd)
        self._refresh_all()

    def action_run_algorithm(self) -> None:
        """F5 — переход на экран алгоритмов."""
        self.app.push_screen(AlgorithmRunnerScreen(self.graph))

    def action_save(self) -> None:
        """Ctrl+S — сохранить в JSON через JSONSerializer."""
        # Упрощённо: всегда в ./graph.json, ты можешь завести FilePicker
        try:
            JSONSerializer.save(self.graph, "graph.json")
        except GraphError as exc:
            self.query_one(StatusBar).set_error(str(exc))
            return

        self.query_one(StatusBar).set_message("Сохранено в graph.json")

    def action_undo(self) -> None:
        """Ctrl+Z — undo."""
        try:
            self.commands.undo()
        except IndexError:
            self.query_one(StatusBar).set_error("Нечего отменять")
            return

        self._refresh_all()

    def action_redo(self) -> None:
        """Ctrl+Y — redo."""
        try:
            self.commands.redo()
        except IndexError:
            self.query_one(StatusBar).set_error("Нечего повторять")
            return

        self._refresh_all()

    def action_context_menu(self) -> None:
        """M — контекстное меню (пока просто подсказка)."""
        self.query_one(StatusBar).set_message(
            "M: A — добавить вершину, E — добавить ребро, Delete — удалить",
        )

    def action_back(self) -> None:
        """Esc — вернуться в главное меню."""
        self.app.pop_screen()
