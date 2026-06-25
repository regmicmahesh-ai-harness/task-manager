"""Domain models for the task manager."""

import uuid
from datetime import UTC, datetime

from pydantic import BaseModel, Field

from shared.enums import CardPriority


def _short_uuid() -> str:
    """Generate an 8-char short UUID."""
    return uuid.uuid4().hex[:8]


def _now() -> datetime:
    """Return current UTC datetime."""
    return datetime.now(UTC)


class TimestampMixin(BaseModel):
    """Base mixin with id and timestamps."""

    id: str = Field(default_factory=_short_uuid)
    created_at: datetime = Field(default_factory=_now)
    updated_at: datetime = Field(default_factory=_now)


class Board(TimestampMixin):
    """A board — top-level container."""

    name: str
    description: str = ""
    archived: bool = False


class List(TimestampMixin):
    """A list (column) within a board."""

    name: str
    position: int = 0
    board_id: str


class Card(TimestampMixin):
    """A card (task) within a list."""

    title: str
    description: str = ""
    position: int = 0
    list_id: str
    priority: CardPriority = CardPriority.MEDIUM
    labels: list[str] = Field(default_factory=list)
    due_date: datetime | None = None


class Label(TimestampMixin):
    """A label that can be attached to cards."""

    name: str
    color: str = "#808080"
