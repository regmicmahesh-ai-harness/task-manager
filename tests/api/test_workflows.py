"""End-to-end workflow tests — exercises the exact flows the TUI uses.

These tests verify that every TUI operation works correctly through
the API: board + default columns, card CRUD into default columns,
move between columns, cascade deletes, and no status field anywhere.
"""

from httpx import AsyncClient


async def _create_board(client: AsyncClient, name: str = "Sprint") -> dict:
    """Create a board and return its JSON response."""
    resp = await client.post(
        "/api/v1/boards", json={"name": name}
    )
    assert resp.status_code == 201
    return resp.json()


async def _get_default_columns(
    client: AsyncClient, board_id: str
) -> list[dict]:
    """Get the auto-created default columns for a board."""
    resp = await client.get(f"/api/v1/boards/{board_id}/lists")
    assert resp.status_code == 200
    return resp.json()


# ── Card create into default columns (the original bug) ───────


async def test_create_card_in_default_todo_column(
    client: AsyncClient,
) -> None:
    """Card can be created in the auto-generated 'To Do' column."""
    board = await _create_board(client)
    cols = await _get_default_columns(client, board["id"])
    todo_col = next(c for c in cols if c["name"] == "To Do")
    resp = await client.post(
        "/api/v1/cards",
        json={"title": "Fix login", "list_id": todo_col["id"]},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == "Fix login"
    assert data["list_id"] == todo_col["id"]
    assert "status" not in data


async def test_create_card_no_status_field_in_response(
    client: AsyncClient,
) -> None:
    """Card response never contains a status field."""
    board = await _create_board(client)
    cols = await _get_default_columns(client, board["id"])
    resp = await client.post(
        "/api/v1/cards",
        json={"title": "Task", "list_id": cols[0]["id"]},
    )
    assert resp.status_code == 201
    assert "status" not in resp.json()


async def test_create_card_with_all_fields(
    client: AsyncClient,
) -> None:
    """Card create with title, desc, priority, labels — no status."""
    board = await _create_board(client)
    cols = await _get_default_columns(client, board["id"])
    resp = await client.post(
        "/api/v1/cards",
        json={
            "title": "Full card",
            "list_id": cols[0]["id"],
            "description": "A detailed task",
            "priority": "urgent",
            "labels": ["bug", "critical"],
        },
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["description"] == "A detailed task"
    assert data["priority"] == "urgent"
    assert data["labels"] == ["bug", "critical"]


# ── Card edit (PATCH) without status ──────────────────────────


async def test_edit_card_title_and_priority(
    client: AsyncClient,
) -> None:
    """PATCH card with title + priority works without status."""
    board = await _create_board(client)
    cols = await _get_default_columns(client, board["id"])
    card = await client.post(
        "/api/v1/cards",
        json={"title": "Old", "list_id": cols[0]["id"]},
    )
    card_id = card.json()["id"]
    resp = await client.patch(
        f"/api/v1/cards/{card_id}",
        json={"title": "New title", "priority": "high"},
    )
    assert resp.status_code == 200
    assert resp.json()["title"] == "New title"
    assert resp.json()["priority"] == "high"
    assert "status" not in resp.json()


# ── Card move between default columns ─────────────────────────


async def test_move_card_between_default_columns(
    client: AsyncClient,
) -> None:
    """Move card from To Do to In Progress (the core TUI flow)."""
    board = await _create_board(client)
    cols = await _get_default_columns(client, board["id"])
    todo = next(c for c in cols if c["name"] == "To Do")
    in_prog = next(c for c in cols if c["name"] == "In Progress")

    card = await client.post(
        "/api/v1/cards",
        json={"title": "Task", "list_id": todo["id"]},
    )
    card_id = card.json()["id"]

    resp = await client.post(
        f"/api/v1/cards/{card_id}/move",
        json={"to_list_id": in_prog["id"]},
    )
    assert resp.status_code == 200
    assert resp.json()["list_id"] == in_prog["id"]

    # Verify it's no longer in To Do
    todo_cards = await client.get(
        "/api/v1/cards", params={"list_id": todo["id"]}
    )
    assert all(c["id"] != card_id for c in todo_cards.json())

    # Verify it's in In Progress
    prog_cards = await client.get(
        "/api/v1/cards", params={"list_id": in_prog["id"]}
    )
    assert any(c["id"] == card_id for c in prog_cards.json())


# ── Delete card ───────────────────────────────────────────────


async def test_delete_card_from_column(client: AsyncClient) -> None:
    """Delete a card, verify it's gone from the column."""
    board = await _create_board(client)
    cols = await _get_default_columns(client, board["id"])
    card = await client.post(
        "/api/v1/cards",
        json={"title": "Delete me", "list_id": cols[0]["id"]},
    )
    card_id = card.json()["id"]

    resp = await client.delete(f"/api/v1/cards/{card_id}")
    assert resp.status_code == 204

    get_resp = await client.get(f"/api/v1/cards/{card_id}")
    assert get_resp.status_code == 404

    list_resp = await client.get(
        "/api/v1/cards", params={"list_id": cols[0]["id"]}
    )
    assert all(c["id"] != card_id for c in list_resp.json())


# ── Board delete cascades ─────────────────────────────────────


async def test_delete_board_cascades_columns_and_cards(
    client: AsyncClient,
) -> None:
    """Deleting a board removes its columns and all cards."""
    board = await _create_board(client)
    board_id = board["id"]
    cols = await _get_default_columns(client, board_id)

    # Add cards to two different columns
    c1 = await client.post(
        "/api/v1/cards",
        json={"title": "Card 1", "list_id": cols[0]["id"]},
    )
    c2 = await client.post(
        "/api/v1/cards",
        json={"title": "Card 2", "list_id": cols[1]["id"]},
    )

    resp = await client.delete(f"/api/v1/boards/{board_id}")
    assert resp.status_code == 204

    # Board gone
    assert (await client.get(f"/api/v1/boards/{board_id}")).status_code == 404
    # Cards gone
    assert (await client.get(f"/api/v1/cards/{c1.json()['id']}")).status_code == 404
    assert (await client.get(f"/api/v1/cards/{c2.json()['id']}")).status_code == 404


# ── Column delete cascades cards ──────────────────────────────


async def test_delete_column_cascades_cards(
    client: AsyncClient,
) -> None:
    """Deleting a column removes all cards in it."""
    board = await _create_board(client)
    board_id = board["id"]
    cols = await _get_default_columns(client, board_id)
    col = cols[0]

    card = await client.post(
        "/api/v1/cards",
        json={"title": "Orphan", "list_id": col["id"]},
    )
    card_id = card.json()["id"]

    resp = await client.delete(
        f"/api/v1/boards/{board_id}/lists/{col['id']}"
    )
    assert resp.status_code == 204
    assert (await client.get(f"/api/v1/cards/{card_id}")).status_code == 404


# ── Full TUI workflow ─────────────────────────────────────────


async def test_full_tui_workflow(client: AsyncClient) -> None:
    """Simulate the complete TUI user journey.

    1. Create board (gets default columns)
    2. Create card in To Do
    3. Edit card (change title + priority)
    4. Move card To Do → In Progress
    5. Move card In Progress → Done
    6. Delete card
    7. Delete board (cascade cleans up)
    """
    # 1. Create board
    board = await _create_board(client, "TUI Test")
    board_id = board["id"]
    cols = await _get_default_columns(client, board_id)
    assert len(cols) == 3
    todo = next(c for c in cols if c["name"] == "To Do")
    in_prog = next(c for c in cols if c["name"] == "In Progress")
    done = next(c for c in cols if c["name"] == "Done")

    # 2. Create card
    card_resp = await client.post(
        "/api/v1/cards",
        json={
            "title": "Implement feature",
            "list_id": todo["id"],
            "priority": "medium",
        },
    )
    assert card_resp.status_code == 201
    card_id = card_resp.json()["id"]

    # 3. Edit card
    edit_resp = await client.patch(
        f"/api/v1/cards/{card_id}",
        json={"title": "Implement auth", "priority": "high"},
    )
    assert edit_resp.status_code == 200
    assert edit_resp.json()["title"] == "Implement auth"

    # 4. Move To Do → In Progress
    move1 = await client.post(
        f"/api/v1/cards/{card_id}/move",
        json={"to_list_id": in_prog["id"]},
    )
    assert move1.json()["list_id"] == in_prog["id"]

    # 5. Move In Progress → Done
    move2 = await client.post(
        f"/api/v1/cards/{card_id}/move",
        json={"to_list_id": done["id"]},
    )
    assert move2.json()["list_id"] == done["id"]

    # 6. Delete card
    del_card = await client.delete(f"/api/v1/cards/{card_id}")
    assert del_card.status_code == 204

    # 7. Delete board (cascade)
    del_board = await client.delete(f"/api/v1/boards/{board_id}")
    assert del_board.status_code == 204
    assert (await client.get(f"/api/v1/boards/{board_id}")).status_code == 404
