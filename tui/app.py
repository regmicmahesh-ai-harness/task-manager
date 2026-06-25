"""Task Manager TUI — Trello-like board view with real-time updates."""

from __future__ import annotations

import os
from typing import Any

import httpx
from textual import work
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.reactive import reactive
from textual.widgets import Footer, Header, Label, Static

API_BASE = os.environ.get("TASK_MANAGER_API_URL", "http://localhost:8000")
API_PREFIX = "/api/v1"

PRIORITY_COLORS = {
    "urgent": "white on red",
    "high": "white on dark_orange3",
    "medium": "white on dodger_blue2",
    "low": "white on grey50",
}

STATUS_ICONS = {
    "todo": "○",
    "in_progress": "◐",
    "done": "●",
    "archived": "◌",
}

REFRESH_INTERVAL = 2.0


def api_get(path: str, params: dict[str, Any] | None = None) -> Any:
    """GET request to the API."""
    try:
        resp = httpx.get(f"{API_BASE}{API_PREFIX}{path}", params=params, timeout=5.0)
        resp.raise_for_status()
        return resp.json()
    except httpx.HTTPError:
        return None


class CardWidget(Static):
    """A single card displayed in a list column."""

    def __init__(self, card: dict[str, Any]) -> None:
        super().__init__()
        self.card_data = card

    def compose(self) -> ComposeResult:
        card = self.card_data
        priority = card.get("priority", "medium")
        status = card.get("status", "todo")
        icon = STATUS_ICONS.get(status, "○")
        title = card.get("title", "Untitled")
        card_id = card.get("id", "")
        desc = card.get("description", "")

        yield Label(f"{icon} {title}", classes="card-title")
        if desc:
            yield Label(desc[:60], classes="card-desc")
        yield Label(f"[{priority}] {card_id}", classes="card-meta")

    def on_mount(self) -> None:
        priority = self.card_data.get("priority", "medium")
        color = PRIORITY_COLORS.get(priority, "white on grey50")
        self.styles.background = color.split(" on ")[-1] if " on " in color else "grey23"


class ListColumn(Vertical):
    """A single list column containing cards."""

    def __init__(self, list_data: dict[str, Any], cards: list[dict[str, Any]]) -> None:
        super().__init__()
        self.list_data = list_data
        self.cards = cards

    def compose(self) -> ComposeResult:
        name = self.list_data.get("name", "Untitled")
        count = len(self.cards)
        yield Label(f" {name} ({count}) ", classes="list-header")
        with VerticalScroll(classes="card-scroll"):
            if self.cards:
                for card in self.cards:
                    yield CardWidget(card)
            else:
                yield Label("No cards", classes="empty-list")


class BoardView(Horizontal):
    """Horizontal layout of list columns — the main Trello-like view."""

    pass


class TaskManagerApp(App):
    """Trello-like TUI for the Task Manager."""

    CSS = """
    Screen {
        background: $surface;
    }

    #board-selector {
        dock: top;
        height: 3;
        background: $primary-darken-2;
        padding: 0 2;
        content-align: center middle;
    }

    #board-selector Label {
        width: auto;
        color: $text;
        text-style: bold;
    }

    #no-connection {
        width: 1fr;
        height: 1fr;
        content-align: center middle;
        text-align: center;
        color: $error;
    }

    BoardView {
        width: 1fr;
        height: 1fr;
        overflow-x: auto;
    }

    ListColumn {
        width: 36;
        min-width: 32;
        max-width: 42;
        height: 1fr;
        margin: 1;
        background: $surface-darken-1;
        border: tall $primary-background;
    }

    .list-header {
        width: 1fr;
        height: 3;
        background: $primary;
        color: $text;
        text-align: center;
        text-style: bold;
        padding: 1 0;
    }

    .card-scroll {
        height: 1fr;
    }

    CardWidget {
        width: 1fr;
        height: auto;
        margin: 1 1 0 1;
        padding: 1;
        background: $surface-lighten-1;
        border: round $primary-background-lighten-1;
    }

    .card-title {
        width: 1fr;
        text-style: bold;
        color: $text;
    }

    .card-desc {
        width: 1fr;
        color: $text-muted;
        margin-top: 1;
    }

    .card-meta {
        width: 1fr;
        color: $text-disabled;
        text-align: right;
        margin-top: 1;
    }

    .empty-list {
        width: 1fr;
        color: $text-disabled;
        text-align: center;
        margin: 2;
    }
    """

    TITLE = "Task Manager"
    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("r", "refresh", "Refresh"),
        Binding("n", "next_board", "Next Board"),
        Binding("p", "prev_board", "Prev Board"),
    ]

    boards: reactive[list[dict[str, Any]]] = reactive(list, always_update=True)
    board_index: reactive[int] = reactive(0)

    def compose(self) -> ComposeResult:
        yield Header()
        yield Horizontal(Label("Loading..."), id="board-selector")
        yield BoardView(id="board-view")
        yield Footer()

    def on_mount(self) -> None:
        """Start loading and auto-refresh."""
        self.load_boards()
        self.set_interval(REFRESH_INTERVAL, self.auto_refresh)

    @work(thread=True)
    def load_boards(self) -> None:
        """Fetch boards from the API."""
        data = api_get("/boards")
        if data is not None:
            self.boards = data
        else:
            self.call_from_thread(self.show_no_connection)

    def show_no_connection(self) -> None:
        """Show connection error."""
        board_view = self.query_one("#board-view", BoardView)
        board_view.remove_children()
        board_view.mount(
            Label("Cannot connect to API\n\nStart the server:\nuvicorn api.main:app --reload", id="no-connection")
        )

    def watch_boards(self, boards: list[dict[str, Any]]) -> None:
        """When boards change, update the selector and load the current board."""
        if not boards:
            return
        if self.board_index >= len(boards):
            self.board_index = 0
        self.update_board_selector()
        self.load_board_content()

    def watch_board_index(self, _index: int) -> None:
        """When board index changes, update view."""
        if self.boards:
            self.update_board_selector()
            self.load_board_content()

    def update_board_selector(self) -> None:
        """Update the board selector label."""
        if not self.boards:
            return
        board = self.boards[self.board_index]
        total = len(self.boards)
        idx = self.board_index + 1
        selector = self.query_one("#board-selector", Horizontal)
        selector.remove_children()
        selector.mount(Label(f"◀ Board {idx}/{total}: {board['name']} ▶"))

    @work(thread=True)
    def load_board_content(self) -> None:
        """Fetch lists and cards for the current board."""
        if not self.boards:
            return
        board = self.boards[self.board_index]
        board_id = board["id"]

        lists_data = api_get(f"/boards/{board_id}/lists")
        if lists_data is None:
            return

        columns: list[tuple[dict[str, Any], list[dict[str, Any]]]] = []
        for lst in lists_data:
            cards = api_get("/cards", params={"list_id": lst["id"]})
            columns.append((lst, cards or []))

        self.call_from_thread(self.render_board, columns)

    def render_board(self, columns: list[tuple[dict[str, Any], list[dict[str, Any]]]]) -> None:
        """Render the board columns."""
        board_view = self.query_one("#board-view", BoardView)
        board_view.remove_children()

        if not columns:
            board_view.mount(Label("No lists in this board. Create one with: task list create", classes="empty-list"))
            return

        for lst, cards in columns:
            board_view.mount(ListColumn(lst, cards))

    def auto_refresh(self) -> None:
        """Periodic refresh."""
        self.load_boards()

    def action_refresh(self) -> None:
        """Manual refresh."""
        self.load_boards()

    def action_next_board(self) -> None:
        """Switch to the next board."""
        if self.boards:
            self.board_index = (self.board_index + 1) % len(self.boards)

    def action_prev_board(self) -> None:
        """Switch to the previous board."""
        if self.boards:
            self.board_index = (self.board_index - 1) % len(self.boards)


def main() -> None:
    """Entry point for the TUI."""
    app = TaskManagerApp()
    app.run()


if __name__ == "__main__":
    main()
