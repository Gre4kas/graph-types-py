# packages/cli/widgets/edge_editor.py
from __future__ import annotations

from typing import Any, Callable

from pydantic import BaseModel, Field, ValidationError
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label, TextArea

SubmitCallback = Callable[[dict[str, Any]], None]


class EdgeForm(BaseModel):
    source: str = Field(min_length=1)
    target: str = Field(min_length=1)
    weight: float | None = 1.0
    attributes_raw: str | None = None

    @property
    def attributes(self) -> dict[str, Any]:
        if not self.attributes_raw:
            return {}
        try:
            import json

            return json.loads(self.attributes_raw)
        except Exception:
            return {}


class EdgeEditorModal(ModalScreen[None]):
    """Модальное окно добавления/редактирования ребра."""

    def __init__(
        self,
        existing_vertices: list[Any],
        on_submit: SubmitCallback,
    ) -> None:
        super().__init__()
        self._on_submit = on_submit
        self._existing = [str(v) for v in existing_vertices]

    def compose(self) -> ComposeResult:
        with Vertical(id="edge-editor"):
            yield Label("Добавить ребро", id="title")
            yield Input(placeholder="source", id="edge-source")
            yield Input(placeholder="target", id="edge-target")
            yield Input(placeholder="weight (float, опционально)", id="edge-weight")
            yield TextArea(
                placeholder='Атрибуты, JSON, напр. {"label":"e1"}',
                id="edge-attrs",
                height=3,
            )
            with Horizontal():
                yield Button("OK", variant="primary", id="btn-ok")
                yield Button("Cancel", id="btn-cancel")

    def on_mount(self) -> None:
        self.query_one("#edge-source", Input).focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-cancel":
            self.app.pop_screen()
            return

        if event.button.id == "btn-ok":
            source = self.query_one("#edge-source", Input).value.strip()
            target = self.query_one("#edge-target", Input).value.strip()
            weight_str = self.query_one("#edge-weight", Input).value.strip()
            attrs_raw = self.query_one("#edge-attrs", TextArea).text

            weight: float | None
            if weight_str:
                try:
                    weight = float(weight_str)
                except ValueError:
                    weight = 1.0
            else:
                weight = 1.0

            try:
                form = EdgeForm(
                    source=source,
                    target=target,
                    weight=weight,
                    attributes_raw=attrs_raw,
                )
            except ValidationError:
                self.app.bell()
                return

            payload = {
                "source": form.source,
                "target": form.target,
                "weight": form.weight,
                "attributes": form.attributes,
            }
            self._on_submit(payload)
            self.app.pop_screen()
