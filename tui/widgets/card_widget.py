"""Card widget — a single card rendered in a list column.

Vim-style keybindings (active when a card is focused):
  j/k    — navigate cards (handled by app)
  e      — edit card via $EDITOR (handled by app)
  x      — delete card
  m      — enter move mode (then h=left, l=right to move card)
  Esc    — back to column-level navigation (handled by app)
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from textual.message import Message
from textual.widgets import Static

if TYPE_CHECKING:
    from textual.events import Key

from tui.config import PRIORITY_COLORS


class CardWidget(Static):
    """A single card displayed in a list column.

    Keyboard-only interaction via vim-style keys.
    """

    can_focus = True

    # ── Messages ────────────────────────────────────────────

    class EditRequested(Message):
        """Fired when 'e' is pressed on a focused card."""

        def __init__(self, card_data: dict[str, Any]) -> None:
            super().__init__()
            self.card_data = card_data

    class DeleteRequested(Message):
        """Fired when 'x' is pressed on a focused card."""

        def __init__(self, card_data: dict[str, Any]) -> None:
            super().__init__()
            self.card_data = card_data

    class MoveLeftRequested(Message):
        """Fired when 'mh' is pressed on a focused card."""

        def __init__(self, card_data: dict[str, Any]) -> None:
            super().__init__()
            self.card_data = card_data

    class MoveRightRequested(Message):
        """Fired when 'ml' is pressed on a focused card."""

        def __init__(self, card_data: dict[str, Any]) -> None:
            super().__init__()
            self.card_data = card_data

    def __init__(self, card: dict[str, Any]) -> None:
        self._card_data = card
        self._move_pending = False
        priority = card.get("priority", "medium")
        title = card.get("title", "Untitled")
        card_id = card.get("id", "")
        desc = card.get("description", "")

        parts = [f"[bold]{title}[/bold]"]
        if desc:
            parts.append(f"  {desc[:60]}")
        parts.append(f"  \\[{priority}] {card_id}")
        super().__init__("\n".join(parts), markup=True)
        self._priority = priority

    @property
    def card_data(self) -> dict[str, Any]:
        """Expose card data for external access."""
        return self._card_data

    def on_mount(self) -> None:
        """Apply priority-based background color."""
        bg = PRIORITY_COLORS.get(self._priority, "gray")
        self.styles.background = bg

    # ── Key handling ────────────────────────────────────────

    def on_key(self, event: Key) -> None:
        """Handle card-level vim keys. j/k/h/l/Esc bubble to app."""
        key = event.key
        if key == "e":
            event.stop()
            event.prevent_default()
            self._move_pending = False
            self.post_message(self.EditRequested(self._card_data))
        elif key == "x":
            event.stop()
            event.prevent_default()
            self._move_pending = False
            self.post_message(self.DeleteRequested(self._card_data))
        elif key == "m":
            event.stop()
            event.prevent_default()
            self._move_pending = True
        elif key == "h" and self._move_pending:
            event.stop()
            event.prevent_default()
            self._move_pending = False
            self.post_message(self.MoveLeftRequested(self._card_data))
        elif key == "l" and self._move_pending:
            event.stop()
            event.prevent_default()
            self._move_pending = False
            self.post_message(self.MoveRightRequested(self._card_data))
        elif key == "escape" and self._move_pending:
            event.stop()
            event.prevent_default()
            self._move_pending = False
