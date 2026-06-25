"""Tests for health check endpoint and shared models."""

import contextlib

from httpx import AsyncClient

from shared.enums import DEFAULT_COLUMNS, CardPriority
from shared.models import Board, Card, Label, List


async def test_health_check(client: AsyncClient) -> None:
    """Health endpoint returns ok."""
    resp = await client.get("/api/v1/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_shared_models_board() -> None:
    """Board model has defaults."""
    b = Board(name="Test")
    assert b.name == "Test"
    assert b.description == ""
    assert b.archived is False
    assert len(b.id) == 8
    assert b.created_at is not None


def test_shared_models_list() -> None:
    """List model has defaults."""
    lst = List(name="Col", board_id="abc12345")
    assert lst.name == "Col"
    assert lst.position == 0
    assert lst.board_id == "abc12345"


def test_shared_models_card() -> None:
    """Card model has defaults."""
    c = Card(title="Task", list_id="abc12345")
    assert c.title == "Task"
    assert c.priority == CardPriority.MEDIUM
    assert c.labels == []
    assert c.due_date is None


def test_shared_models_label() -> None:
    """Label model has defaults."""
    lbl = Label(name="bug")
    assert lbl.color == "#808080"


async def test_get_db_dependency() -> None:
    """Direct test of get_db dependency."""
    from api.dependencies import get_db

    gen = get_db()
    session = await gen.__anext__()
    assert session is not None
    with contextlib.suppress(StopAsyncIteration):
        await gen.__anext__()


async def test_app_lifespan() -> None:
    """App lifespan creates tables."""
    from api.main import app, lifespan

    async with lifespan(app):
        pass  # Tables created and cleaned up


def test_shared_enums() -> None:
    """Enum values are correct."""
    assert CardPriority.LOW == "low"
    assert CardPriority.MEDIUM == "medium"
    assert CardPriority.HIGH == "high"
    assert CardPriority.URGENT == "urgent"
    assert DEFAULT_COLUMNS == ["To Do", "In Progress", "Done"]
