"""Modal for creating a new list (column) in a board."""

from __future__ import annotations

from textual import work
from textual.app import ComposeResult
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label

from tui.api_client import api_post


class CreateListModal(ModalScreen[bool]):
    """Modal dialog to create a new list in the current board."""

    def __init__(self, board_id: str, board_name: str) -> None:
        super().__init__()
        self._board_id = board_id
        self._board_name = board_name

    BINDINGS = [("escape", "cancel", "Cancel")]

    def compose(self) -> ComposeResult:
        """Build the modal form."""
        with Vertical(id="modal-dialog"):
            yield Label(f"Add Column to '{self._board_name}'", id="modal-title")
            yield Label("Name")
            yield Input(placeholder="Column name", id="list-name")
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
        name = self.query_one("#list-name", Input).value.strip()
        if not name:
            self.notify("Name is required", severity="error")
            return
        result = await api_post(
            f"/boards/{self._board_id}/lists",
            json={"name": name, "board_id": self._board_id},
        )
        if result is not None:
            self.notify(f"Column '{name}' created")
            self.dismiss(True)
        else:
            self.notify("Failed to create column", severity="error")

    def action_cancel(self) -> None:
        """Dismiss on escape."""
        self.dismiss(False)
