"""Modal for creating a new board."""

from __future__ import annotations

from textual import work
from textual.app import ComposeResult
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label

from tui.api_client import api_post


class CreateBoardModal(ModalScreen[bool]):
    """Modal dialog to create a new board."""

    BINDINGS = [("escape", "cancel", "Cancel")]

    def compose(self) -> ComposeResult:
        """Build the modal form."""
        with Vertical(id="modal-dialog"):
            yield Label("Create Board", id="modal-title")
            yield Label("Name")
            yield Input(placeholder="Board name", id="board-name")
            yield Label("Description")
            yield Input(placeholder="Description (optional)", id="board-desc")
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
        name = self.query_one("#board-name", Input).value.strip()
        if not name:
            self.notify("Name is required", severity="error")
            return
        desc = self.query_one("#board-desc", Input).value.strip()
        result = await api_post("/boards", json={"name": name, "description": desc})
        if result is not None:
            self.notify(f"Board '{name}' created")
            self.dismiss(True)
        else:
            self.notify("Failed to create board", severity="error")

    def action_cancel(self) -> None:
        """Dismiss on escape."""
        self.dismiss(False)
