"""Modal for moving a card to a different list."""

from __future__ import annotations

from typing import Any

from textual import work
from textual.app import ComposeResult
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Label, Select

from tui.api_client import api_post


class MoveCardModal(ModalScreen[bool]):
    """Modal dialog to move a card to another list."""

    BINDINGS = [("escape", "cancel", "Cancel")]

    def __init__(
        self,
        card_data: dict[str, Any],
        available_lists: list[dict[str, Any]],
    ) -> None:
        super().__init__()
        self._card = card_data
        self._lists = available_lists

    def compose(self) -> ComposeResult:
        """Build the move form."""
        title = self._card.get("title", "Untitled")
        current_list_id = self._card.get("list_id", "")
        options = [
            (lst["name"], lst["id"])
            for lst in self._lists
            if lst["id"] != current_list_id
        ]
        with Vertical(id="modal-dialog"):
            yield Label(f"Move '{title}'", id="modal-title")
            yield Label("Target Column")
            if options:
                yield Select(options, id="target-list")
            else:
                yield Label("No other columns available")
            with Vertical(id="modal-buttons"):
                yield Button("Move", variant="primary", id="btn-move")
                yield Button("Cancel", id="btn-cancel")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button clicks."""
        if event.button.id == "btn-move":
            self._do_move()
        else:
            self.dismiss(False)

    @work
    async def _do_move(self) -> None:
        """Send move request to API."""
        card_id = self._card["id"]
        try:
            target = self.query_one("#target-list", Select)
        except Exception:
            self.notify("No target column selected", severity="error")
            return
        if target.value is Select.BLANK:
            self.notify("Select a target column", severity="error")
            return
        result = await api_post(
            f"/cards/{card_id}/move",
            json={"to_list_id": str(target.value)},
        )
        if result is not None:
            self.notify("Card moved")
            self.dismiss(True)
        else:
            self.notify("Failed to move card", severity="error")

    def action_cancel(self) -> None:
        """Dismiss on escape."""
        self.dismiss(False)
