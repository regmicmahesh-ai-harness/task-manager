"""Tests for board endpoints."""

from httpx import AsyncClient


async def test_create_board(client: AsyncClient) -> None:
    """Create a board."""
    resp = await client.post("/api/v1/boards", json={"name": "Sprint 1", "description": "First sprint"})
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "Sprint 1"
    assert data["description"] == "First sprint"
    assert data["archived"] is False
    assert "id" in data


async def test_create_board_minimal(client: AsyncClient) -> None:
    """Create a board with only name."""
    resp = await client.post("/api/v1/boards", json={"name": "Minimal"})
    assert resp.status_code == 201
    assert resp.json()["description"] == ""


async def test_create_board_validation_error(client: AsyncClient) -> None:
    """Name is required and cannot be empty."""
    resp = await client.post("/api/v1/boards", json={"name": ""})
    assert resp.status_code == 422


async def test_list_boards_empty(client: AsyncClient) -> None:
    """List boards when none exist."""
    resp = await client.get("/api/v1/boards")
    assert resp.status_code == 200
    assert resp.json() == []


async def test_list_boards(client: AsyncClient) -> None:
    """List boards after creating some."""
    await client.post("/api/v1/boards", json={"name": "Board 1"})
    await client.post("/api/v1/boards", json={"name": "Board 2"})
    resp = await client.get("/api/v1/boards")
    assert resp.status_code == 200
    assert len(resp.json()) == 2


async def test_list_boards_pagination(client: AsyncClient) -> None:
    """Pagination works."""
    for i in range(5):
        await client.post("/api/v1/boards", json={"name": f"Board {i}"})
    resp = await client.get("/api/v1/boards", params={"limit": 2, "offset": 0})
    assert len(resp.json()) == 2
    resp2 = await client.get("/api/v1/boards", params={"limit": 2, "offset": 3})
    assert len(resp2.json()) == 2


async def test_list_boards_filter_archived(client: AsyncClient) -> None:
    """Filter by archived status."""
    r1 = await client.post("/api/v1/boards", json={"name": "Active"})
    r2 = await client.post("/api/v1/boards", json={"name": "Old"})
    await client.patch(f"/api/v1/boards/{r2.json()['id']}", json={"archived": True})
    resp = await client.get("/api/v1/boards", params={"archived": False})
    assert len(resp.json()) == 1
    assert resp.json()[0]["name"] == "Active"


async def test_get_board(client: AsyncClient) -> None:
    """Get a board by ID."""
    create = await client.post("/api/v1/boards", json={"name": "My Board"})
    board_id = create.json()["id"]
    resp = await client.get(f"/api/v1/boards/{board_id}")
    assert resp.status_code == 200
    assert resp.json()["name"] == "My Board"


async def test_get_board_not_found(client: AsyncClient) -> None:
    """Get nonexistent board returns 404."""
    resp = await client.get("/api/v1/boards/nonexist")
    assert resp.status_code == 404


async def test_update_board(client: AsyncClient) -> None:
    """Update board fields."""
    create = await client.post("/api/v1/boards", json={"name": "Old Name"})
    board_id = create.json()["id"]
    resp = await client.patch(
        f"/api/v1/boards/{board_id}",
        json={"name": "New Name", "description": "Updated", "archived": True},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "New Name"
    assert data["description"] == "Updated"
    assert data["archived"] is True


async def test_update_board_partial(client: AsyncClient) -> None:
    """Partial update only changes provided fields."""
    create = await client.post("/api/v1/boards", json={"name": "Keep", "description": "Desc"})
    board_id = create.json()["id"]
    resp = await client.patch(f"/api/v1/boards/{board_id}", json={"archived": True})
    data = resp.json()
    assert data["name"] == "Keep"
    assert data["description"] == "Desc"
    assert data["archived"] is True


async def test_update_board_not_found(client: AsyncClient) -> None:
    """Update nonexistent board returns 404."""
    resp = await client.patch("/api/v1/boards/nonexist", json={"name": "X"})
    assert resp.status_code == 404


async def test_delete_board(client: AsyncClient) -> None:
    """Delete a board."""
    create = await client.post("/api/v1/boards", json={"name": "Delete Me"})
    board_id = create.json()["id"]
    resp = await client.delete(f"/api/v1/boards/{board_id}")
    assert resp.status_code == 204
    get_resp = await client.get(f"/api/v1/boards/{board_id}")
    assert get_resp.status_code == 404


async def test_delete_board_not_found(client: AsyncClient) -> None:
    """Delete nonexistent board returns 404."""
    resp = await client.delete("/api/v1/boards/nonexist")
    assert resp.status_code == 404
