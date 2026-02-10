# packages/cli/commands/graph_commands.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol, TYPE_CHECKING

if TYPE_CHECKING:
    from packages.core.base_graph import BaseGraph
    from packages.representations.base_representation import BaseRepresentation
    from packages.core.vertex import Vertex


class Command(Protocol):
    def execute(self) -> None: ...
    def undo(self) -> None: ...


@dataclass
class AddVertexCommand:
    graph: BaseGraph
    vertex: Vertex
    _done: bool = False

    def execute(self) -> None:
        if not self._done:
            self.graph.add_vertex(self.vertex.id, **self.vertex.attributes)
            self._done = True

    def undo(self) -> None:
        if self._done:
            self.graph.remove_vertex(self.vertex.id)
            self._done = False


@dataclass
class RemoveVertexCommand:
    graph: BaseGraph
    vertex_id: Any
    _snapshot: dict[str, Any] | None = None

    def execute(self) -> None:
        # Сохраним атрибуты вершины (для undo)
        v = self.graph.get_vertex(self.vertex_id)
        self._snapshot = {"id": v.id, "attributes": v.attributes.copy()}
        self.graph.remove_vertex(self.vertex_id)

    def undo(self) -> None:
        if self._snapshot is None:
            return
        self.graph.add_vertex(
            self._snapshot["id"],
            **self._snapshot["attributes"],
        )


@dataclass
class AddEdgeCommand:
    graph: BaseGraph
    source: Any
    target: Any
    weight: float = 1.0
    attributes: dict[str, Any] | None = None
    _done: bool = False

    def execute(self) -> None:
        attrs = self.attributes or {}
        self.graph.add_edge(self.source, self.target, weight=self.weight, **attrs)
        self._done = True

    def undo(self) -> None:
        if self._done:
            self.graph.remove_edge(self.source, self.target)
            self._done = False


@dataclass
class RemoveEdgeCommand:
    graph: BaseGraph
    source: Any
    target: Any
    _snapshot: dict[str, Any] | None = None

    def execute(self) -> None:
        e = self.graph.get_edge(self.source, self.target)
        self._snapshot = {
            "source": e.source,
            "target": e.target,
            "weight": e.weight,
            "attributes": e.attributes.copy(),
        }
        self.graph.remove_edge(self.source, self.target)

    def undo(self) -> None:
        if self._snapshot is None:
            return
        self.graph.add_edge(
            self._snapshot["source"],
            self._snapshot["target"],
            weight=self._snapshot["weight"],
            **self._snapshot["attributes"],
        )


@dataclass
class ChangeRepresentationCommand:
    graph: BaseGraph
    old_repr: BaseRepresentation
    new_repr: BaseRepresentation

    def execute(self) -> None:
        # Представление уже применено конвертером
        pass

    def undo(self) -> None:
        # В идеале тут snapshot до смены, минимально:
        self.graph.set_representation(self.old_repr)


class CommandHistory:
    """Простейший стек команд с undo/redo."""

    def __init__(self) -> None:
        self._done: list[Command] = []
        self._undone: list[Command] = []

    def push(self, command: Command) -> None:
        self._done.append(command)
        self._undone.clear()

    def undo(self) -> None:
        if not self._done:
            raise IndexError("No commands to undo")
        cmd = self._done.pop()
        cmd.undo()
        self._undone.append(cmd)

    def redo(self) -> None:
        if not self._undone:
            raise IndexError("No commands to redo")
        cmd = self._undone.pop()
        cmd.execute()
        self._done.append(cmd)
