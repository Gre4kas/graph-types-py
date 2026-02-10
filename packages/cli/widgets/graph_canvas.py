# packages/cli/widgets/graph_canvas.py
from __future__ import annotations

import math
import random
from typing import Any, TYPE_CHECKING

from rich.segment import Segment
from rich.style import Style
from rich.text import Text
from textual.widget import Widget
from textual.geometry import Size

if TYPE_CHECKING:
    from rich.console import Console, ConsoleOptions, RenderResult
    from packages.core.base_graph import BaseGraph


class GraphCanvas(Widget):
    """
    ASCII/Unicode visualization of the graph.
    
    Layouts:
    - Circular for |V| <= 20
    - Force-directed (simplified) for |V| > 20
    
    Safety:
    - Implements boundary checks to prevent IndexError.
    """

    DEFAULT_CSS = """
    GraphCanvas {
        border: round cyan;
        height: 1fr;
        width: 1fr;
        background: $surface-darken-1;
    }
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._graph: BaseGraph | None = None
        self._highlighted: set[Any] = set()

    def set_graph(self, graph: BaseGraph) -> None:
        self._graph = graph
        self.refresh()

    def set_highlighted(self, vertices: set[Any]) -> None:
        self._highlighted = vertices
        self.refresh()

    def render(self) -> RenderResult:
        if self._graph is None:
            return Text("No graph loaded.", style="dim")

        # Get available size, default to reasonable minimums
        width = max(self.content_size.width, 40)
        height = max(self.content_size.height, 20)

        vertices = list(self._graph.vertices())
        n = len(vertices)
        
        if n == 0:
            return Text("Graph is empty", style="dim")

        # Layout allocation
        if n <= 20:
            positions = self._circular_layout(n, width, height)
        else:
            positions = self._force_layout(n, width, height)

        # Map ID to Position
        id_to_pos: dict[Any, tuple[int, int]] = {}
        for i, v in enumerate(vertices):
            # Ensure index is within positions bounds
            if i < len(positions):
                id_to_pos[v.id] = positions[i]

        # Init canvas grid
        # Note: height is rows, width is cols
        canvas = [[" " for _ in range(width)] for _ in range(height)]

        # Draw Edges first (so vertices are on top)
        for edge in self._graph.edges():
            if edge.source in id_to_pos and edge.target in id_to_pos:
                sx, sy = id_to_pos[edge.source]
                tx, ty = id_to_pos[edge.target]
                self._draw_line(canvas, sx, sy, tx, ty)

        # Draw Vertices
        for v in vertices:
            if v.id in id_to_pos:
                x, y = id_to_pos[v.id]
                
                is_highlighted = v.id in self._highlighted
                symbol = "●"
                # Draw label if space permits
                label = str(v.id)[:5]
                
                # Manual drawing of symbol
                # For proper color support in a low-level char canvas, we would need 
                # a parallel color buffer or use Rich's Canvas.
                # Here we simulate highlight with a different char or just rely on Rich Text later?
                # Actually, since we construct Rich Text lines at the end, we can't easily color *one* char
                # without processing the buffer into segments.
                # Workaround: Use different symbol for highlighted.
                if is_highlighted:
                    symbol = "★" 
                    # If we really want color, we need a list of Segments instead of strings in canvas.
                    # But for now, let's use symbol.
                
                self._put_char(canvas, x, y, symbol)
                self._put_text(canvas, x + 1, y, label)

        # Convert to Rich Text
        lines: list[Text] = []
        for row in canvas:
            line_str = "".join(row)
            lines.append(Text(line_str))

        return Text("\n").join(lines)

    # ----- Layout Algorithms -----

    def _circular_layout(
        self,
        n: int,
        width: int,
        height: int,
    ) -> list[tuple[int, int]]:
        """Arrange vertices in a circle."""
        cx, cy = width // 2, height // 2
        # Radius: fit in smallest dimension, minus padding
        radius = min(width, height * 2) // 2 - 4
        if radius < 2:
            radius = 2

        positions: list[tuple[int, int]] = []
        for i in range(n):
            angle = 2 * math.pi * i / n
            # Aspect ratio correction for terminal char (approx 1:2)
            x = int(cx + radius * math.cos(angle) * 2) 
            y = int(cy + radius * math.sin(angle))
            
            # Clamp
            x = max(1, min(width - 2, x))
            y = max(1, min(height - 2, y))
            positions.append((x, y))
            
        return positions

    def _force_layout(
        self,
        n: int,
        width: int,
        height: int,
    ) -> list[tuple[int, int]]:
        """Simple force-directed layout simulation."""
        # Initial random positions
        random.seed(42)
        pad = 4
        # Store as float for calculation
        pos_f = [
            [float(random.randint(pad, width - pad)), float(random.randint(pad, height - pad))]
            for _ in range(n)
        ]

        # Simple repulsive force
        iterations = 50
        # Optimal distance
        k = math.sqrt((width * height) / n)
        
        for _ in range(iterations):
            # Limit iterations for performance on large graphs
            if n > 100: 
                break

            # Calculate forces (Repulsion only for simplicity in text mode)
            for i in range(n):
                disp_x, disp_y = 0.0, 0.0
                for j in range(n):
                    if i == j: continue
                    
                    dx = pos_f[i][0] - pos_f[j][0]
                    dy = pos_f[i][1] - pos_f[j][1]
                    dist = math.sqrt(dx*dx + dy*dy) + 0.1
                    
                    # Repulsive force: f = k^2 / d
                    f = (k * k) / dist
                    disp_x += (dx / dist) * f
                    disp_y += (dy / dist) * f
                
                # Apply displacement (capped)
                length = math.sqrt(disp_x*disp_x + disp_y*disp_y) + 0.1
                pos_f[i][0] += (disp_x / length) * min(length, k)
                pos_f[i][1] += (disp_y / length) * min(length, k)
                
                # Keep in bounds
                pos_f[i][0] = max(2, min(width - 2, pos_f[i][0]))
                pos_f[i][1] = max(2, min(height - 2, pos_f[i][1]))

        return [(int(x), int(y)) for x, y in pos_f]

    # ----- Drawing Primitives (Safe) -----

    def _put_char(self, canvas: list[list[str]], x: int, y: int, char: str) -> None:
        """Safely place a character on the canvas."""
        if 0 <= y < len(canvas) and 0 <= x < len(canvas[0]):
            canvas[y][x] = char

    def _put_text(self, canvas: list[list[str]], x: int, y: int, text: str) -> None:
        """Safely place text."""
        if not (0 <= y < len(canvas)):
            return
        
        row_width = len(canvas[0])
        for i, char in enumerate(text):
            if 0 <= x + i < row_width:
                canvas[y][x + i] = char

    def _draw_line(
        self,
        canvas: list[list[str]],
        x0: int,
        y0: int,
        x1: int,
        y1: int,
    ) -> None:
        """Bresenham's line algorithm."""
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy

        # Max iterations to prevent infinite loops in case of logic error
        max_iter = max(dx, dy) * 2 + 10
        
        while max_iter > 0:
            self._put_char(canvas, x0, y0, "·")
            
            if x0 == x1 and y0 == y1:
                break
            
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy
            
            max_iter -= 1
