# packages/cli/widgets/graph_canvas.py
from __future__ import annotations

import math
import random
from typing import Any, TYPE_CHECKING

from rich.console import Console, ConsoleOptions, RenderResult
from rich.segment import Segment
from rich.style import Style
from rich.text import Text
from textual.widget import Widget

if TYPE_CHECKING:
    from packages.core.base_graph import BaseGraph


class GraphCanvas(Widget):
    """
    ASCII/Unicode визуализация графа.

    Для |V| <= 20 — круговое размещение.
    Для |V| > 20 — псевдо-force-directed (несколько итераций "отталкивания").
    """

    DEFAULT_CSS = """
    GraphCanvas {
        border: round cyan;
        height: 1fr;
        width: 1fr;
    }
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._graph: BaseGraph | None = None

    def set_graph(self, graph: BaseGraph) -> None:
        self._graph = graph
        self.refresh()

    def render(self) -> RenderResult:
        if self._graph is None:
            return Text("Нет графа для отображения", style="dim")

        width = max(self.size.width, 20)
        height = max(self.size.height, 10)

        vertices = list(self._graph.vertices())
        n = len(vertices)
        if n == 0:
            return Text("Граф пуст", style="dim")

        # Рассчитать позиции
        if n <= 20:
            positions = self._circular_layout(n, width, height)
        else:
            positions = self._random_layout(n, width, height)

        # Словарь: vertex.id -> (x, y)
        id_to_pos: dict[Any, tuple[int, int]] = {
            v.id: positions[i] for i, v in enumerate(vertices)
        }

        # Буфер символов
        canvas = [[" " for _ in range(width)] for _ in range(height)]

        # Рёбра (очень грубо: соединяем прямыми линиями по сетке)
        for edge in self._graph.edges():
            sx, sy = id_to_pos[edge.source]
            tx, ty = id_to_pos[edge.target]
            self._draw_edge(canvas, sx, sy, tx, ty, edge=edge)

        # Вершины
        for v in vertices:
            x, y = id_to_pos[v.id]
            self._put_char(canvas, x, y, "●")

        # Собираем Rich Text
        lines: list[Text] = []
        for row in canvas:
            line = "".join(row).rstrip()
            lines.append(Text(line))

        return Text("\n").join(lines)

    # ----- Layouts -----

    def _circular_layout(
        self,
        n: int,
        width: int,
        height: int,
    ) -> list[tuple[int, int]]:
        """Круговое размещение."""
        cx = width // 2
        cy = height // 2
        r = min(width, height) // 2 - 2
        if r < 2:
            r = 2

        positions: list[tuple[int, int]] = []
        for i in range(n):
            angle = 2 * math.pi * i / n
            x = int(cx + r * math.cos(angle))
            y = int(cy + r * math.sin(angle))
            positions.append((max(1, min(width - 2, x)), max(1, min(height - 2, y))))
        return positions

    def _random_layout(
        self,
        n: int,
        width: int,
        height: int,
    ) -> list[tuple[int, int]]:
        """Примитивный random + несколько шагов "отталкивания"."""
        random.seed(42)
        positions = [
            (random.randint(1, width - 2), random.randint(1, height - 2))
            for _ in range(n)
        ]

        for _ in range(3):  # 3 итерации
            for i in range(n):
                xi, yi = positions[i]
                dx = dy = 0
                for j in range(n):
                    if i == j:
                        continue
                    xj, yj = positions[j]
                    vx = xi - xj
                    vy = yi - yj
                    dist2 = vx * vx + vy * vy + 1e-3
                    force = 10 / dist2
                    dx += vx * force
                    dy += vy * force
                xi = int(max(1, min(width - 2, xi + dx)))
                yi = int(max(1, min(height - 2, yi + dy)))
                positions[i] = (xi, yi)

        return positions

    # ----- Drawing helpers -----

    def _put_char(self, canvas: list[list[str]], x: int, y: int, ch: str) -> None:
        if 0 <= y < len(canvas) and 0 <= x < len(canvas[0]):
            canvas[y][x] = ch

    def _draw_edge(
        self,
        canvas: list[list[str]],
        sx: int,
        sy: int,
        tx: int,
        ty: int,
        edge: Any,
    ) -> None:
        """Очень простая Bresenham-like линия с box-drawing."""
        dx = abs(tx - sx)
        dy = -abs(ty - sy)
        sx_step = 1 if sx < tx else -1
        sy_step = 1 if sy < ty else -1
        err = dx + dy

        x, y = sx, sy
        while True:
            self._put_char(canvas, x, y, "─")
            if x == tx and y == ty:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x += sx_step
            if e2 <= dx:
                err += dx
                y += sy_step
