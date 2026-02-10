# packages/cli/widgets/status_bar.py
from __future__ import annotations

from typing import Any

from textual.widgets import Static


class StatusBar(Static):
    """Статусная строка с текущим состоянием."""

    DEFAULT_CSS = """
    StatusBar {
        height: 1;
        content-align: left middle;
        color: white;
        background: #303030;
    }
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._base_message = ""
        self._warning = ""
        self._error = ""
        self._graph_info = ""

    def set_graph_info(
        self,
        graph_type: str,
        directed: bool,
        representation: str,
    ) -> None:
        self._graph_info = f"{graph_type} | {'directed' if directed else 'undirected'} | {representation}"
        self._refresh_ui()

    def set_message(self, message: str) -> None:
        self._base_message = message
        self._error = ""
        self._refresh_ui()

    def set_warning(self, message: str) -> None:
        self._warning = message
        self._error = ""
        self._refresh_ui()

    def set_error(self, message: str) -> None:
        self._error = message
        self._refresh_ui()

    def _refresh_ui(self) -> None:
        parts: list[str] = []
        if self._graph_info:
            parts.append(self._graph_info)
        if self._base_message:
            parts.append(f" · {self._base_message}")
        if self._warning:
            parts.append(f" · ⚠ {self._warning}")
        if self._error:
            parts.append(f" · ⛔ {self._error}")

        self.update("".join(parts))
