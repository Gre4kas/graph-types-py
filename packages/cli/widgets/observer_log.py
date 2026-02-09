# packages/cli/widgets/observer_log.py
from __future__ import annotations

from datetime import datetime
from typing import Any

from textual.widgets import Static


class ObserverLog(Static):
    """Виджет лога изменений графа."""

    DEFAULT_CSS = """
    ObserverLog {
        border: round green;
        height: 5;
        overflow: hidden;
    }
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._entries: list[str] = []

    def add_entry(self, message: str, timestamp: bool = False) -> None:
        if timestamp:
            ts = datetime.now().strftime("%H:%M:%S")
            entry = f"[{ts}] {message}"
        else:
            entry = message

        self._entries.append(entry)
        self._entries = self._entries[-10:]  # последние 10
        self.update("\n".join(self._entries))
