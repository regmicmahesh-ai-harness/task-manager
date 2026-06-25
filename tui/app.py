"""Task Manager TUI — Trello-like board view.

Three-tier vim navigation:
  BOARD level  — h/l switch boards, j/Enter dive into columns
  COLUMN level — h/l switch columns, j/Enter dive into cards, Esc back to board
  CARD level   — j/k move between cards, Esc back to column
                 e=edit ($EDITOR), x=delete, m then h/l=move card

  b — new board     L — new column    c — new card
  d — delete board  r — refresh       q — quit
"""

from __future__ import annotations

import os
import subprocess
import tempfile
from enum import StrEnum
from typing import Any

import yaml
from textual import work
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal
from textual.events import Key
from textual.widgets import Footer, Header, Label, Static

from tui.api_client import api_get, api_patch, api_post
from tui.modals import (
    ConfirmDeleteModal,
    CreateBoardModal,
    CreateCardModal,
    CreateListModal,
)
from tui.styles import APP_CSS
from tui.widgets import BoardView, ListColumn
from tui.widgets.card_widget import CardWidget
from tui.widgets.list_column import ColumnHeader


class _NavLevel(StrEnum):
    """Current navigation tier."""

    BOARD = "board"
    COLUMN = "column"
    CARD = "card"


class BoardSelector(Static):
    """Focusable board selector bar for vim navigation."""

    can_focus = True


class TaskManagerApp(App):
    """Trello-like TUI for the Task Manager."""

    CSS = APP_CSS
    TITLE = "Task Manager"
    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("r", "refresh", "Refresh"),
        Binding("b", "create_board", "New Board"),
        Binding("L", "create_list", "New Column"),
        Binding("c", "create_card", "New Card"),
        Binding("d", "delete_board", "Del Board"),
    ]

    def __init__(self) -> None:
        super().__init__()
        self._boards: list[dict[str, Any]] = []
        self._board_index: int = 0
        self._current_lists: list[dict[str, Any]] = []
        self._col_index: int = 0
        self._card_index: int = 0
        self._nav_level = _NavLevel.BOARD

    def compose(self) -> ComposeResult:
        """Build the main layout."""
        yield Header()
        yield Horizontal(
            BoardSelector("Loading...", id="board-label"),
            id="board-selector",
        )
        yield BoardView(id="board-view")
        yield Footer()

    def on_mount(self) -> None:
        """Load initial data. Press 'r' to refresh manually."""
        self.load_data()

    # ── Vim navigation ─────────────────────────────────────────

    def on_key(self, event: Key) -> None:
        """Three-tier hjkl navigation."""
        key = event.key
        if self._nav_level == _NavLevel.BOARD:
            self._handle_board_key(event, key)
        elif self._nav_level == _NavLevel.COLUMN:
            self._handle_column_key(event, key)
        elif self._nav_level == _NavLevel.CARD:
            self._handle_card_key(event, key)

    def _handle_board_key(self, event: Key, key: str) -> None:
        """Board level: h/l=switch boards, j/Enter=dive into columns."""
        if key == "h":
            event.stop()
            event.prevent_default()
            self._switch_board(-1)
        elif key == "l":
            event.stop()
            event.prevent_default()
            self._switch_board(1)
        elif key in ("j", "enter"):
            event.stop()
            event.prevent_default()
            self._enter_column_level()

    def _handle_column_key(self, event: Key, key: str) -> None:
        """Column level: h/l=switch columns, j/Enter=dive, Esc/k=back."""
        if key == "h":
            event.stop()
            event.prevent_default()
            self._nav_column(-1)
        elif key == "l":
            event.stop()
            event.prevent_default()
            self._nav_column(1)
        elif key in ("j", "enter"):
            event.stop()
            event.prevent_default()
            self._enter_card_level()
        elif key in ("escape", "k"):
            event.stop()
            event.prevent_default()
            self._back_to_board_level()

    def _handle_card_key(self, event: Key, key: str) -> None:
        """Card level: j/k=move, Esc=back to columns."""
        if key == "j":
            event.stop()
            event.prevent_default()
            self._nav_card(1)
        elif key == "k":
            event.stop()
            event.prevent_default()
            self._nav_card(-1)
        elif key == "escape":
            event.stop()
            event.prevent_default()
            self._back_to_column_level()

    # ── Board-level helpers ────────────────────────────────────

    def _switch_board(self, direction: int) -> None:
        """Switch to next/prev board and reload."""
        if not self._boards:
            return
        self._board_index = (self._board_index + direction) % len(
            self._boards
        )
        self._col_index = 0
        self._card_index = 0
        self.load_data()

    def _focus_board_selector(self) -> None:
        """Focus the board selector bar."""
        try:
            self.query_one("#board-label", BoardSelector).focus()
        except Exception:
            pass

    def _enter_column_level(self) -> None:
        """Dive from board into columns."""
        columns = self._get_columns()
        if not columns:
            self.notify("No columns on this board", severity="warning")
            return
        self._nav_level = _NavLevel.COLUMN
        self._col_index = 0
        self._focus_column_header()

    def _back_to_board_level(self) -> None:
        """Go back to board-level navigation."""
        self._nav_level = _NavLevel.BOARD
        self._col_index = 0
        self._card_index = 0
        self._focus_board_selector()

    # ── Column-level helpers ───────────────────────────────────

    def _get_columns(self) -> list[ListColumn]:
        """Get all ListColumn widgets in the board view."""
        try:
            return list(
                self.query_one("#board-view", BoardView).query(ListColumn)
            )
        except Exception:
            return []

    def _get_cards_in_column(self, col: ListColumn) -> list[CardWidget]:
        """Get all CardWidget children in a column."""
        return list(col.query(CardWidget))

    def _nav_column(self, direction: int) -> None:
        """Move focus between column headers."""
        columns = self._get_columns()
        if not columns:
            return
        self._col_index = max(
            0, min(self._col_index + direction, len(columns) - 1)
        )
        self._focus_column_header()

    def _focus_column_header(self) -> None:
        """Focus the header of the current column."""
        columns = self._get_columns()
        if not columns:
            return
        self._col_index = min(self._col_index, len(columns) - 1)
        col = columns[self._col_index]
        headers = list(col.query(ColumnHeader))
        if headers:
            headers[0].focus()

    def _enter_card_level(self) -> None:
        """Dive from column header into the cards."""
        columns = self._get_columns()
        if not columns:
            return
        self._col_index = min(self._col_index, len(columns) - 1)
        cards = self._get_cards_in_column(columns[self._col_index])
        if cards:
            self._nav_level = _NavLevel.CARD
            self._card_index = 0
            cards[0].focus()
        else:
            self.notify("No cards in this column", severity="warning")

    def _back_to_column_level(self) -> None:
        """Go back from card level to column level."""
        self._nav_level = _NavLevel.COLUMN
        self._card_index = 0
        self._focus_column_header()

    # ── Card-level helpers ─────────────────────────────────────

    def _nav_card(self, direction: int) -> None:
        """Move focus between cards in the current column."""
        columns = self._get_columns()
        if not columns:
            return
        self._col_index = min(self._col_index, len(columns) - 1)
        cards = self._get_cards_in_column(columns[self._col_index])
        if not cards:
            return
        self._card_index = max(
            0, min(self._card_index + direction, len(cards) - 1)
        )
        cards[self._card_index].focus()

    def _focus_current(self) -> None:
        """Re-focus at current position after data reload."""
        if self._nav_level == _NavLevel.BOARD:
            self._focus_board_selector()
        elif self._nav_level == _NavLevel.COLUMN:
            columns = self._get_columns()
            if columns:
                self._focus_column_header()
            else:
                self._back_to_board_level()
        else:
            columns = self._get_columns()
            if not columns:
                self._back_to_board_level()
                return
            self._col_index = min(self._col_index, len(columns) - 1)
            cards = self._get_cards_in_column(columns[self._col_index])
            if cards:
                self._card_index = min(self._card_index, len(cards) - 1)
                cards[self._card_index].focus()
            else:
                self._back_to_column_level()

    # ── Data loading ───────────────────────────────────────────

    @work(exclusive=True)
    async def load_data(self) -> None:
        """Fetch boards, lists, and cards from the API."""
        data = await api_get("/boards")
        if data is None:
            self._show_no_connection()
            return

        self._boards = data
        if not self._boards:
            self._update_board_selector()
            board_view = self.query_one("#board-view", BoardView)
            await board_view.remove_children()
            await board_view.mount(
                Label(
                    "No boards yet — press [b]b[/b] to create one",
                    classes="empty-list",
                    markup=True,
                )
            )
            return

        if self._board_index >= len(self._boards):
            self._board_index = 0

        self._update_board_selector()
        board = self._boards[self._board_index]

        lists_data = await api_get(f"/boards/{board['id']}/lists")
        if lists_data is None:
            return

        self._current_lists = lists_data
        columns: list[tuple[dict[str, Any], list[dict[str, Any]]]] = []
        for lst in lists_data:
            cards = await api_get("/cards", params={"list_id": lst["id"]})
            columns.append((lst, cards or []))

        self._render_board(columns)
        self.call_after_refresh(self._focus_current)

    # ── UI helpers ─────────────────────────────────────────────

    def _show_no_connection(self) -> None:
        board_view = self.query_one("#board-view", BoardView)
        board_view.remove_children()
        board_view.mount(
            Label(
                "Cannot connect to API\n\n"
                "Start the server:\nuvicorn api.main:app --reload",
                id="no-connection",
            )
        )

    def _update_board_selector(self) -> None:
        """Update the board selector text."""
        try:
            label = self.query_one("#board-label", BoardSelector)
        except Exception:
            return
        if not self._boards:
            label.update("No boards")
            return
        board = self._boards[self._board_index]
        total = len(self._boards)
        idx = self._board_index + 1
        label.update(f"◀ Board {idx}/{total}: {board['name']} ▶")

    def _render_board(
        self,
        columns: list[tuple[dict[str, Any], list[dict[str, Any]]]],
    ) -> None:
        board_view = self.query_one("#board-view", BoardView)
        board_view.remove_children()
        if not columns:
            board_view.mount(
                Label(
                    "No columns — press [b]L[/b] to add one",
                    classes="empty-list",
                    markup=True,
                )
            )
            return
        for lst, cards in columns:
            board_view.mount(ListColumn(lst, cards))

    # ── Card interactions (vim keys) ──────────────────────────

    def on_card_widget_edit_requested(
        self, event: CardWidget.EditRequested
    ) -> None:
        """Edit card via $EDITOR on a YAML temp file (k9s style)."""
        self._edit_card_in_editor(event.card_data)

    @work(thread=True)
    def _edit_card_in_editor(self, card: dict[str, Any]) -> None:
        """Suspend TUI, open $EDITOR, parse result, PATCH the API."""
        editable = {
            "title": card.get("title", ""),
            "description": card.get("description", ""),
            "priority": card.get("priority", "medium"),
        }
        editor = os.environ.get("EDITOR", "vi")
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".yaml", prefix="task-card-", delete=False
        ) as tmp:
            yaml.dump(editable, tmp, default_flow_style=False)
            tmp_path = tmp.name

        try:
            with self.suspend():
                subprocess.run([editor, tmp_path], check=True)

            with open(tmp_path) as f:
                updated = yaml.safe_load(f)

            if not isinstance(updated, dict):
                self.notify("Invalid YAML — edit aborted", severity="error")
                return

            title = str(updated.get("title", "")).strip()
            if not title:
                self.notify("Title is required", severity="error")
                return

            body: dict[str, Any] = {
                "title": title,
                "description": str(updated.get("description", "")),
                "priority": str(updated.get("priority", "medium")),
            }
            if body == editable:
                self.notify("No changes")
                return

            self.call_from_thread(self._patch_card, card["id"], body)
        finally:
            os.unlink(tmp_path)

    @work
    async def _patch_card(self, card_id: str, body: dict[str, Any]) -> None:
        """Send PATCH to API and reload."""
        result = await api_patch(f"/cards/{card_id}", json=body)
        if result is not None:
            self.notify(f"Card '{body['title']}' updated")
            self.load_data()
        else:
            self.notify("Failed to update card", severity="error")

    def on_card_widget_delete_requested(
        self, event: CardWidget.DeleteRequested
    ) -> None:
        """Open delete confirmation when 'x' is pressed on a card."""
        card = event.card_data
        self.push_screen(
            ConfirmDeleteModal(
                "Card",
                card.get("title", ""),
                f"/cards/{card['id']}",
            ),
            callback=self._on_modal_dismiss,
        )

    def on_card_widget_move_left_requested(
        self, event: CardWidget.MoveLeftRequested
    ) -> None:
        """Move card to the previous (left) column."""
        self._move_card_direction(event.card_data, -1)

    def on_card_widget_move_right_requested(
        self, event: CardWidget.MoveRightRequested
    ) -> None:
        """Move card to the next (right) column."""
        self._move_card_direction(event.card_data, 1)

    @work
    async def _move_card_direction(
        self, card: dict[str, Any], direction: int
    ) -> None:
        """Move a card left (-1) or right (+1) by one column."""
        current_list_id = card.get("list_id", "")
        col_ids = [lst["id"] for lst in self._current_lists]
        if current_list_id not in col_ids:
            self.notify("Cannot determine current column", severity="error")
            return
        idx = col_ids.index(current_list_id)
        target_idx = idx + direction
        if target_idx < 0 or target_idx >= len(col_ids):
            label = "left" if direction < 0 else "right"
            self.notify(f"No column to the {label}", severity="warning")
            return
        target_list_id = col_ids[target_idx]
        result = await api_post(
            f"/cards/{card['id']}/move",
            json={"to_list_id": target_list_id},
        )
        if result is not None:
            self.notify("Card moved")
            self.load_data()
        else:
            self.notify("Failed to move card", severity="error")

    def _on_modal_dismiss(self, changed: bool | None) -> None:
        if changed:
            self.load_data()

    # ── Actions ────────────────────────────────────────────────

    def action_refresh(self) -> None:
        """Manual refresh."""
        self.load_data()

    def action_create_board(self) -> None:
        """Open create-board modal."""
        self.push_screen(CreateBoardModal(), callback=self._on_modal_dismiss)

    def action_create_list(self) -> None:
        """Open create-list modal for the current board."""
        if not self._boards:
            self.notify("Create a board first", severity="warning")
            return
        board = self._boards[self._board_index]
        self.push_screen(
            CreateListModal(board["id"], board["name"]),
            callback=self._on_modal_dismiss,
        )

    def action_create_card(self) -> None:
        """Open create-card modal for the current column."""
        if not self._boards:
            self.notify("Create a board first", severity="warning")
            return
        if not self._current_lists:
            self.notify("No columns available", severity="warning")
            return
        col_idx = min(self._col_index, len(self._current_lists) - 1)
        lst = self._current_lists[col_idx]
        self.push_screen(
            CreateCardModal(lst["id"], lst["name"]),
            callback=self._on_modal_dismiss,
        )

    def action_delete_board(self) -> None:
        """Delete the current board."""
        if not self._boards:
            self.notify("No board to delete", severity="warning")
            return
        board = self._boards[self._board_index]
        self.push_screen(
            ConfirmDeleteModal(
                "Board", board["name"], f"/boards/{board['id']}"
            ),
            callback=self._on_modal_dismiss,
        )


def main() -> None:
    """Entry point for the TUI."""
    app = TaskManagerApp()
    app.run()


if __name__ == "__main__":
    main()
