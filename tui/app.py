"""Task Manager TUI — Trello-like board view with real-time updates."""

from __future__ import annotations

import os
from typing import Any

import httpx
from textual import work
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.widgets import Footer, Header, Label, Static

API_BASE = os.environ.get("TASK_MANAGER_API_URL", "http://localhost:8000")
API_PREFIX = "/api/v1"

PRIORITY_COLORS = {
    "urgent": "red",
    "high": "dark_orange3",
    "medium": "dodger_blue2",
    "low": "grey50",
}

STATUS_ICONS = {
    "todo": "○",
    "in_progress": "◐",
    "done": "●",
    "archived": "◌",
}

REFRESH_INTERVAL = 2.0


async def api_get(path: str, params: dict[str, Any] | None = None) -> Any:
    """Async GET request to the API."""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(f"{API_BASE}{API_PREFIX}{path}", params=params)
            resp.raise_for_status()
            return resp.json()
    except httpx.HTTPError:
        return None


class CardWidget(Static):
    """A single card displayed in a list column."""

    def __init__(self, card: dict[str, Any]) -> None:
        priority = card.get("priority", "medium")
        status = card.get("status", "todo")
        icon = STATUS_ICONS.get(status, "○")
        title = card.get("title", "Untitled")
        card_id = card.get("id", "")
        desc = card.get("description", "")

        parts = [f"{icon} [bold]{title}[/bold]"]
        if desc:
            parts.append(f"  {desc[:60]}")
        parts.append(f"  \\[{priority}] {card_id}")
        super().__init__("\n".join(parts), markup=True)
        self._priority = priority

    def on_mount(self) -> None:
        bg = PRIORITY_COLORS.get(self._priority, "grey50")
        self.styles.background = bg


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

    def __init__(self) -> None:
        super().__init__()
        self._boards: list[dict[str, Any]] = []
        self._board_index: int = 0

    def compose(self) -> ComposeResult:
        yield Header()
        yield Horizontal(Label("Loading..."), id="board-selector")
        yield BoardView(id="board-view")
        yield Footer()

    def on_mount(self) -> None:
        """Start loading and auto-refresh."""
        self.load_data()
        self.set_interval(REFRESH_INTERVAL, self.load_data)

    @work(exclusive=True)
    async def load_data(self) -> None:
        """Fetch boards, lists, and cards from the API."""
        data = await api_get("/boards")
        if data is None:
            self.show_no_connection()
            return

        self._boards = data
        if not self._boards:
            self.update_board_selector()
            board_view = self.query_one("#board-view", BoardView)
            await board_view.remove_children()
            await board_view.mount(
                Label(
                    "No boards. Create one with: task board create --name 'My Board'",
                    classes="empty-list",
                )
            )
            return

        if self._board_index >= len(self._boards):
            self._board_index = 0

        self.update_board_selector()

        board = self._boards[self._board_index]
        board_id = board["id"]

        lists_data = await api_get(f"/boards/{board_id}/lists")
        if lists_data is None:
            return

        columns: list[tuple[dict[str, Any], list[dict[str, Any]]]] = []
        for lst in lists_data:
            cards = await api_get("/cards", params={"list_id": lst["id"]})
            columns.append((lst, cards or []))

        self.render_board(columns)

    def show_no_connection(self) -> None:
        """Show connection error."""
        board_view = self.query_one("#board-view", BoardView)
        board_view.remove_children()
        board_view.mount(
            Label(
                "Cannot connect to API\n\nStart the server:\nuvicorn api.main:app --reload",
                id="no-connection",
            )
        )

    def update_board_selector(self) -> None:
        """Update the board selector label."""
        selector = self.query_one("#board-selector", Horizontal)
        selector.remove_children()
        if not self._boards:
            selector.mount(Label("No boards"))
            return
        board = self._boards[self._board_index]
        total = len(self._boards)
        idx = self._board_index + 1
        selector.mount(Label(f"◀ Board {idx}/{total}: {board['name']} ▶"))

    def render_board(self, columns: list[tuple[dict[str, Any], list[dict[str, Any]]]]) -> None:
        """Render the board columns."""
        board_view = self.query_one("#board-view", BoardView)
        board_view.remove_children()

        if not columns:
            board_view.mount(
                Label(
                    "No lists in this board. Create one with: task list create",
                    classes="empty-list",
                )
            )
            return

        for lst, cards in columns:
            board_view.mount(ListColumn(lst, cards))

    def action_refresh(self) -> None:
        """Manual refresh."""
        self.load_data()

    def action_next_board(self) -> None:
        """Switch to the next board."""
        if self._boards:
            self._board_index = (self._board_index + 1) % len(self._boards)
            self.load_data()

    def action_prev_board(self) -> None:
        """Switch to the previous board."""
        if self._boards:
            self._board_index = (self._board_index - 1) % len(self._boards)
            self.load_data()


def main() -> None:
    """Entry point for the TUI."""
    app = TaskManagerApp()
    app.run()


if __name__ == "__main__":
    main()
