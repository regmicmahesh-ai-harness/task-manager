"""List column widget — a vertical column of cards."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from textual.containers import Vertical, VerticalScroll
from textual.widgets import Label, Static

if TYPE_CHECKING:
    from textual.app import ComposeResult

from tui.widgets.card_widget import CardWidget


class ColumnHeader(Static):
    """Focusable column header for two-tier vim navigation."""

    can_focus = True


class ListColumn(Vertical):
    """A single list column containing cards."""

    def __init__(self, list_data: dict[str, Any], cards: list[dict[str, Any]]) -> None:
        super().__init__()
        self.list_data = list_data
        self.cards = cards

    def compose(self) -> ComposeResult:
        """Render header and card list."""
        name = self.list_data.get("name", "Untitled")
        count = len(self.cards)
        yield ColumnHeader(f" {name} ({count}) ", classes="list-header")
        with VerticalScroll(classes="card-scroll"):
            if self.cards:
                for card in self.cards:
                    yield CardWidget(card)
            else:
                yield Label("No cards", classes="empty-list")
