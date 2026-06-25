"""Request/response schemas for the task manager API."""

from datetime import datetime

from pydantic import BaseModel, Field

from shared.enums import CardPriority

# ── Board ──────────────────────────────────────────────────────────


class BoardCreate(BaseModel):
    """Create a new board."""

    name: str = Field(min_length=1, max_length=100)
    description: str = ""


class BoardUpdate(BaseModel):
    """Update an existing board."""

    name: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = None
    archived: bool | None = None


class BoardResponse(BaseModel):
    """Board response."""

    id: str
    name: str
    description: str
    archived: bool
    created_at: datetime
    updated_at: datetime


# ── List ───────────────────────────────────────────────────────────


class ListCreate(BaseModel):
    """Create a new list."""

    name: str = Field(min_length=1, max_length=100)
    position: int = 0
    board_id: str


class ListUpdate(BaseModel):
    """Update an existing list."""

    name: str | None = Field(default=None, min_length=1, max_length=100)
    position: int | None = None


class ListResponse(BaseModel):
    """List response."""

    id: str
    name: str
    position: int
    board_id: str
    created_at: datetime
    updated_at: datetime


# ── Card ───────────────────────────────────────────────────────────


class CardCreate(BaseModel):
    """Create a new card."""

    title: str = Field(min_length=1, max_length=200)
    description: str = ""
    position: int = 0
    list_id: str
    priority: CardPriority = CardPriority.MEDIUM
    labels: list[str] = Field(default_factory=list)
    due_date: datetime | None = None


class CardUpdate(BaseModel):
    """Update an existing card."""

    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = None
    position: int | None = None
    priority: CardPriority | None = None
    labels: list[str] | None = None
    due_date: datetime | None = None


class CardMove(BaseModel):
    """Move a card to a different list."""

    to_list_id: str
    position: int = 0


class BulkCardMove(BaseModel):
    """Move multiple cards."""

    card_ids: list[str]
    to_list_id: str


class CardResponse(BaseModel):
    """Card response."""

    id: str
    title: str
    description: str
    position: int
    list_id: str
    priority: CardPriority
    labels: list[str]
    due_date: datetime | None
    created_at: datetime
    updated_at: datetime


# ── Pagination ─────────────────────────────────────────────────────


class PaginationParams(BaseModel):
    """Pagination query parameters."""

    limit: int = Field(default=50, ge=1, le=100)
    offset: int = Field(default=0, ge=0)
