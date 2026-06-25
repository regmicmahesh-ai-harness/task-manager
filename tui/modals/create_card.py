"""Modal for creating a new card in the current column."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from textual import work
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label, Select

if TYPE_CHECKING:
    from textual.app import ComposeResult

from tui.api_client import api_post

PRIORITIES = [
    ("Low", "low"),
    ("Medium", "medium"),
    ("High", "high"),
    ("Urgent", "urgent"),
]


class CreateCardModal(ModalScreen[bool]):
    """Modal dialog to create a new card in a specific column."""

    BINDINGS = [("escape", "cancel", "Cancel")]

    def __init__(self, list_id: str, list_name: str) -> None:
        super().__init__()
        self._list_id = list_id
        self._list_name = list_name

    def compose(self) -> ComposeResult:
        """Build the create-card form."""
        with Vertical(id="modal-dialog"):
            yield Label(f"Create Card in '{self._list_name}'", id="modal-title")
            yield Label("Title")
            yield Input(placeholder="Card title", id="card-title")
            yield Label("Description")
            yield Input(placeholder="Description (optional)", id="card-desc")
            yield Label("Priority")
            yield Select(PRIORITIES, value="medium", id="card-priority")
            with Vertical(id="modal-buttons"):
                yield Button("Create", variant="primary", id="btn-create")
                yield Button("Cancel", id="btn-cancel")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button clicks."""
        if event.button.id == "btn-create":
            self._do_create()
        else:
            self.dismiss(False)

    @work
    async def _do_create(self) -> None:
        """Send create request to API."""
        title = self.query_one("#card-title", Input).value.strip()
        if not title:
            self.notify("Title is required", severity="error")
            return
        body: dict[str, Any] = {
            "title": title,
            "list_id": self._list_id,
            "description": self.query_one("#card-desc", Input).value,
            "priority": self.query_one("#card-priority", Select).value,
        }
        result = await api_post("/cards", json=body)
        if result is not None:
            self.notify(f"Card '{title}' created")
            self.dismiss(True)
        else:
            self.notify("Failed to create card", severity="error")

    def action_cancel(self) -> None:
        """Dismiss on escape."""
        self.dismiss(False)
