"""Tests for card endpoints."""

from httpx import AsyncClient


async def _setup(client: AsyncClient) -> tuple[str, str]:
    """Create a board and list, return (board_id, list_id)."""
    b = await client.post("/api/v1/boards", json={"name": "Board"})
    board_id = b.json()["id"]
    lst = await client.post(
        f"/api/v1/boards/{board_id}/lists",
        json={"name": "To Do", "board_id": board_id},
    )
    return board_id, lst.json()["id"]


async def test_create_card(client: AsyncClient) -> None:
    """Create a card."""
    _, list_id = await _setup(client)
    resp = await client.post(
        "/api/v1/cards",
        json={"title": "Task 1", "list_id": list_id, "priority": "high"},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == "Task 1"
    assert data["list_id"] == list_id
    assert data["priority"] == "high"
    assert data["status"] == "todo"


async def test_create_card_with_labels(client: AsyncClient) -> None:
    """Create a card with labels."""
    _, list_id = await _setup(client)
    resp = await client.post(
        "/api/v1/cards",
        json={"title": "Labeled", "list_id": list_id, "labels": ["bug", "urgent"]},
    )
    assert resp.status_code == 201
    assert resp.json()["labels"] == ["bug", "urgent"]


async def test_create_card_list_not_found(client: AsyncClient) -> None:
    """Create card with nonexistent list returns 404."""
    resp = await client.post("/api/v1/cards", json={"title": "Orphan", "list_id": "nonexist"})
    assert resp.status_code == 404


async def test_create_card_validation_error(client: AsyncClient) -> None:
    """Empty title fails validation."""
    _, list_id = await _setup(client)
    resp = await client.post("/api/v1/cards", json={"title": "", "list_id": list_id})
    assert resp.status_code == 422


async def test_list_cards(client: AsyncClient) -> None:
    """List all cards."""
    _, list_id = await _setup(client)
    await client.post("/api/v1/cards", json={"title": "A", "list_id": list_id})
    await client.post("/api/v1/cards", json={"title": "B", "list_id": list_id})
    resp = await client.get("/api/v1/cards")
    assert resp.status_code == 200
    assert len(resp.json()) == 2


async def test_list_cards_filter_by_list(client: AsyncClient) -> None:
    """Filter cards by list_id."""
    board_resp = await client.post("/api/v1/boards", json={"name": "Board"})
    board_id = board_resp.json()["id"]
    l1 = await client.post(
        f"/api/v1/boards/{board_id}/lists",
        json={"name": "L1", "board_id": board_id},
    )
    l2 = await client.post(
        f"/api/v1/boards/{board_id}/lists",
        json={"name": "L2", "board_id": board_id},
    )
    l1_id, l2_id = l1.json()["id"], l2.json()["id"]
    await client.post("/api/v1/cards", json={"title": "In L1", "list_id": l1_id})
    await client.post("/api/v1/cards", json={"title": "In L2", "list_id": l2_id})
    resp = await client.get("/api/v1/cards", params={"list_id": l1_id})
    assert len(resp.json()) == 1
    assert resp.json()[0]["title"] == "In L1"


async def test_list_cards_filter_by_status(client: AsyncClient) -> None:
    """Filter cards by status."""
    _, list_id = await _setup(client)
    await client.post("/api/v1/cards", json={"title": "Todo", "list_id": list_id})
    await client.post(
        "/api/v1/cards",
        json={"title": "Done", "list_id": list_id, "status": "done"},
    )
    resp = await client.get("/api/v1/cards", params={"status": "done"})
    assert len(resp.json()) == 1
    assert resp.json()[0]["title"] == "Done"


async def test_list_cards_filter_by_priority(client: AsyncClient) -> None:
    """Filter cards by priority."""
    _, list_id = await _setup(client)
    await client.post(
        "/api/v1/cards",
        json={"title": "Low", "list_id": list_id, "priority": "low"},
    )
    await client.post(
        "/api/v1/cards",
        json={"title": "High", "list_id": list_id, "priority": "high"},
    )
    resp = await client.get("/api/v1/cards", params={"priority": "high"})
    assert len(resp.json()) == 1
    assert resp.json()[0]["title"] == "High"


async def test_list_cards_pagination(client: AsyncClient) -> None:
    """Pagination on cards."""
    _, list_id = await _setup(client)
    for i in range(5):
        await client.post("/api/v1/cards", json={"title": f"Card {i}", "list_id": list_id})
    resp = await client.get("/api/v1/cards", params={"limit": 2})
    assert len(resp.json()) == 2


async def test_get_card(client: AsyncClient) -> None:
    """Get a card by ID."""
    _, list_id = await _setup(client)
    create = await client.post("/api/v1/cards", json={"title": "Get Me", "list_id": list_id})
    card_id = create.json()["id"]
    resp = await client.get(f"/api/v1/cards/{card_id}")
    assert resp.status_code == 200
    assert resp.json()["title"] == "Get Me"


async def test_get_card_not_found(client: AsyncClient) -> None:
    """Get nonexistent card returns 404."""
    resp = await client.get("/api/v1/cards/nonexist")
    assert resp.status_code == 404


async def test_update_card(client: AsyncClient) -> None:
    """Update card fields."""
    _, list_id = await _setup(client)
    create = await client.post("/api/v1/cards", json={"title": "Old", "list_id": list_id})
    card_id = create.json()["id"]
    resp = await client.patch(
        f"/api/v1/cards/{card_id}",
        json={"title": "New", "status": "done", "priority": "urgent"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["title"] == "New"
    assert data["status"] == "done"
    assert data["priority"] == "urgent"


async def test_update_card_labels(client: AsyncClient) -> None:
    """Update card labels."""
    _, list_id = await _setup(client)
    create = await client.post("/api/v1/cards", json={"title": "Task", "list_id": list_id})
    card_id = create.json()["id"]
    resp = await client.patch(f"/api/v1/cards/{card_id}", json={"labels": ["feature", "v2"]})
    assert resp.json()["labels"] == ["feature", "v2"]


async def test_update_card_not_found(client: AsyncClient) -> None:
    """Update nonexistent card returns 404."""
    resp = await client.patch("/api/v1/cards/nonexist", json={"title": "X"})
    assert resp.status_code == 404


async def test_move_card(client: AsyncClient) -> None:
    """Move a card to a different list."""
    board_resp = await client.post("/api/v1/boards", json={"name": "Board"})
    board_id = board_resp.json()["id"]
    l1 = await client.post(
        f"/api/v1/boards/{board_id}/lists",
        json={"name": "From", "board_id": board_id},
    )
    l2 = await client.post(
        f"/api/v1/boards/{board_id}/lists",
        json={"name": "To", "board_id": board_id},
    )
    l1_id, l2_id = l1.json()["id"], l2.json()["id"]
    create = await client.post("/api/v1/cards", json={"title": "Move Me", "list_id": l1_id})
    card_id = create.json()["id"]
    resp = await client.post(
        f"/api/v1/cards/{card_id}/move",
        json={"to_list_id": l2_id, "position": 3},
    )
    assert resp.status_code == 200
    assert resp.json()["list_id"] == l2_id
    assert resp.json()["position"] == 3


async def test_move_card_not_found(client: AsyncClient) -> None:
    """Move nonexistent card returns 404."""
    resp = await client.post("/api/v1/cards/nonexist/move", json={"to_list_id": "x"})
    assert resp.status_code == 404


async def test_move_card_target_list_not_found(client: AsyncClient) -> None:
    """Move to nonexistent list returns 404."""
    _, list_id = await _setup(client)
    create = await client.post("/api/v1/cards", json={"title": "Card", "list_id": list_id})
    card_id = create.json()["id"]
    resp = await client.post(f"/api/v1/cards/{card_id}/move", json={"to_list_id": "nonexist"})
    assert resp.status_code == 404


async def test_bulk_move_cards(client: AsyncClient) -> None:
    """Bulk move cards."""
    board_resp = await client.post("/api/v1/boards", json={"name": "Board"})
    board_id = board_resp.json()["id"]
    l1 = await client.post(
        f"/api/v1/boards/{board_id}/lists",
        json={"name": "From", "board_id": board_id},
    )
    l2 = await client.post(
        f"/api/v1/boards/{board_id}/lists",
        json={"name": "To", "board_id": board_id},
    )
    l1_id, l2_id = l1.json()["id"], l2.json()["id"]
    c1 = await client.post("/api/v1/cards", json={"title": "C1", "list_id": l1_id})
    c2 = await client.post("/api/v1/cards", json={"title": "C2", "list_id": l1_id})
    resp = await client.post(
        "/api/v1/cards/bulk",
        json={"card_ids": [c1.json()["id"], c2.json()["id"]], "to_list_id": l2_id},
    )
    assert resp.status_code == 200
    assert len(resp.json()) == 2
    for card in resp.json():
        assert card["list_id"] == l2_id


async def test_bulk_move_cards_target_not_found(client: AsyncClient) -> None:
    """Bulk move to nonexistent list returns 404."""
    resp = await client.post(
        "/api/v1/cards/bulk",
        json={"card_ids": ["a", "b"], "to_list_id": "nonexist"},
    )
    assert resp.status_code == 404


async def test_delete_card(client: AsyncClient) -> None:
    """Delete a card."""
    _, list_id = await _setup(client)
    create = await client.post("/api/v1/cards", json={"title": "Delete Me", "list_id": list_id})
    card_id = create.json()["id"]
    resp = await client.delete(f"/api/v1/cards/{card_id}")
    assert resp.status_code == 204
    get_resp = await client.get(f"/api/v1/cards/{card_id}")
    assert get_resp.status_code == 404


async def test_delete_card_not_found(client: AsyncClient) -> None:
    """Delete nonexistent card returns 404."""
    resp = await client.delete("/api/v1/cards/nonexist")
    assert resp.status_code == 404


async def test_create_card_with_due_date(client: AsyncClient) -> None:
    """Create a card with a due date."""
    _, list_id = await _setup(client)
    resp = await client.post(
        "/api/v1/cards",
        json={
            "title": "Deadline",
            "list_id": list_id,
            "due_date": "2025-12-31T23:59:59",
        },
    )
    assert resp.status_code == 201
    assert resp.json()["due_date"] is not None


async def test_update_card_due_date(client: AsyncClient) -> None:
    """Update card due_date including clearing it."""
    _, list_id = await _setup(client)
    create = await client.post(
        "/api/v1/cards",
        json={"title": "T", "list_id": list_id, "due_date": "2025-12-31T00:00:00"},
    )
    card_id = create.json()["id"]
    # Update to null
    resp = await client.patch(f"/api/v1/cards/{card_id}", json={"due_date": None})
    assert resp.status_code == 200
    assert resp.json()["due_date"] is None


async def test_update_card_description(client: AsyncClient) -> None:
    """Update card description and position."""
    _, list_id = await _setup(client)
    create = await client.post("/api/v1/cards", json={"title": "T", "list_id": list_id})
    card_id = create.json()["id"]
    resp = await client.patch(
        f"/api/v1/cards/{card_id}",
        json={"description": "New desc", "position": 5},
    )
    assert resp.json()["description"] == "New desc"
    assert resp.json()["position"] == 5
