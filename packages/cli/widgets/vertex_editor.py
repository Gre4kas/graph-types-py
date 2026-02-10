# packages/cli/widgets/vertex_editor.py
from __future__ import annotations

from typing import Any, Callable, Literal

from pydantic import BaseModel, Field, ValidationError
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label, TextArea

SubmitCallback = Callable[[dict[str, Any]], None]


class VertexForm(BaseModel):
    id: str = Field(min_length=1)
    # простой JSON-like ввод атрибутов, ты можешь заменить на key=value парсер
    attributes_raw: str | None = None

    @property
    def attributes(self) -> dict[str, Any]:
        if not self.attributes_raw:
            return {}
        try:
            import json

            return json.loads(self.attributes_raw)
        except Exception:
            # fallback: пусто, реальную обработку можно усилить
            return {}


class VertexEditorModal(ModalScreen[None]):
    """
    Модальное окно редактирования/создания вершины.

    mode: "create" или "rename"
    """

    def __init__(
        self,
        on_submit: SubmitCallback,
        initial_id: str | None = None,
        mode: Literal["create", "rename"] = "create",
    ) -> None:
        super().__init__()
        self._on_submit = on_submit
        self._initial_id = initial_id
        self._mode = mode

    def compose(self) -> ComposeResult:
        title = "Добавить вершину" if self._mode == "create" else "Переименовать вершину"

        with Vertical(id="vertex-editor"):
            yield Label(title, id="title")
            if self._mode == "rename":
                yield Label(f"Старый ID: {self._initial_id}", id="old-id-label")
            yield Input(placeholder="ID вершины", id="vertex-id")
            if self._mode == "create":
                yield TextArea(
                    placeholder='Атрибуты в формате JSON, напр. {"color":"red"}',
                    id="vertex-attrs",
                    height=3,
                )

            with Horizontal():
                yield Button("OK", variant="primary", id="btn-ok")
                yield Button("Cancel", id="btn-cancel")

    def on_mount(self) -> None:
        if self._initial_id is not None:
            self.query_one("#vertex-id", Input).value = str(self._initial_id)
        self.query_one("#vertex-id", Input).focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-cancel":
            self.app.pop_screen()
            return

        if event.button.id == "btn-ok":
            vid = self.query_one("#vertex-id", Input).value.strip()
            attrs_raw = None
            if self._mode == "create":
                attrs_raw = self.query_one("#vertex-attrs", TextArea).text

            try:
                form = VertexForm(id=vid, attributes_raw=attrs_raw)
            except ValidationError as exc:
                # можно вывести ошибку в отдельный label
                self.app.bell()
                return

            payload: dict[str, Any] = {"id": form.id, "attributes": form.attributes}
            if self._mode == "rename":
                payload["old_id"] = self._initial_id

            self._on_submit(payload)
            self.app.pop_screen()
