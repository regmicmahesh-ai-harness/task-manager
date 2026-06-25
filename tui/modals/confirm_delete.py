"""Reusable confirmation modal for delete operations."""

from __future__ import annotations

from typing import TYPE_CHECKING

from textual import work
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Label

if TYPE_CHECKING:
    from textual.app import ComposeResult

from tui.api_client import api_delete


class ConfirmDeleteModal(ModalScreen[bool]):
    """Generic delete confirmation dialog."""

    BINDINGS = [("escape", "cancel", "Cancel")]

    def __init__(self, entity_type: str, entity_name: str, delete_path: str) -> None:
        super().__init__()
        self._entity_type = entity_type
        self._entity_name = entity_name
        self._delete_path = delete_path

    def compose(self) -> ComposeResult:
        """Build confirmation dialog."""
        with Vertical(id="modal-dialog"):
            yield Label(f"Delete {self._entity_type}", id="modal-title")
            yield Label(f"Are you sure you want to delete '{self._entity_name}'?")
            with Vertical(id="modal-buttons"):
                yield Button("Delete", variant="error", id="btn-delete")
                yield Button("Cancel", id="btn-cancel")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button clicks."""
        if event.button.id == "btn-delete":
            self._do_delete()
        else:
            self.dismiss(False)

    @work
    async def _do_delete(self) -> None:
        """Send delete request to API."""
        ok = await api_delete(self._delete_path)
        if ok:
            self.notify(f"{self._entity_type} '{self._entity_name}' deleted")
            self.dismiss(True)
        else:
            self.notify(
                f"Failed to delete {self._entity_type}",
                severity="error",
            )

    def action_cancel(self) -> None:
        """Dismiss on escape."""
        self.dismiss(False)
