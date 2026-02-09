# packages/cli/screens/representation_switcher.py
from __future__ import annotations

import asyncio
from typing import Any, Callable, TYPE_CHECKING

from textual.app import ComposeResult
from textual.containers import Vertical, Horizontal
from textual.screen import ModalScreen
from textual.widgets import Button, Label, RadioButton, RadioSet

from packages.converters.representation_converters import RepresentationConverter

if TYPE_CHECKING:
    from packages.core.base_graph import BaseGraph
    from packages.representations.base_representation import BaseRepresentation

OnApplied = Callable[[BaseRepresentation, BaseRepresentation], None]


class RepresentationSwitcherModal(ModalScreen[None]):
    """Модальное окно смены представления для уже существующего графа."""

    def __init__(
        self,
        graph: BaseGraph,
        on_applied: OnApplied,
    ) -> None:
        super().__init__()
        self._graph = graph
        self._on_applied = on_applied

    def compose(self) -> ComposeResult:
        with Vertical(id="repr-switcher"):
            yield Label("Сменить представление графа", id="title")
            yield Label(
                "Матрица смежности для |V| > 1000 может быть очень медленной.",
                id="warning",
            )
            yield RadioSet(
                RadioButton("Adjacency List", id="radio_list"),
                RadioButton("Adjacency Matrix", id="radio_matrix"),
                RadioButton("Edge List", id="radio_edge"),
                id="radio_set",
            )
            with Horizontal():
                yield Button("Применить", variant="primary", id="btn-apply")
                yield Button("Отмена", id="btn-cancel")

    def on_mount(self) -> None:
        # Выбрать текущее
        current = self._graph._representation.__class__.__name__.lower()
        rs = self.query_one("#radio_set", RadioSet)
        if "list" in current:
            rs.press_button("radio_list")
        elif "matrix" in current:
            rs.press_button("radio_matrix")
        else:
            rs.press_button("radio_edge")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-cancel":
            self.app.pop_screen()
            return

        if event.button.id == "btn-apply":
            asyncio.create_task(self._apply_async())

    async def _apply_async(self) -> None:
        rs = self.query_one("#radio_set", RadioSet)
        selected = rs.pressed_button
        if selected.id == "radio_list":
            target = "adjacency_list"
        elif selected.id == "radio_matrix":
            target = "adjacency_matrix"
        else:
            target = "edge_list"

        # Тяжёлая операция — в отдельном потоке
        def _convert() -> tuple[BaseRepresentation, BaseRepresentation]:
            old_repr: BaseRepresentation = self._graph._representation
            new_repr = RepresentationConverter.convert(
                self._graph,
                target_representation=target,
            )
            # обычно convert возвращает новый граф/репрезентацию — подстрой под свой API
            return old_repr, new_repr

        old_repr, new_repr = await asyncio.to_thread(_convert)
        # если convert возвращает новый граф, замени _graph._representation и/или graph
        self._on_applied(old_repr, new_repr)
        self.app.pop_screen()
