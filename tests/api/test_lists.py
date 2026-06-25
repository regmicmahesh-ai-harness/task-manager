"""Tests for list endpoints."""

from httpx import AsyncClient


async def _create_board(client: AsyncClient) -> str:
    """Helper: create a board and return its ID."""
    resp = await client.post("/api/v1/boards", json={"name": "Test Board"})
    return resp.json()["id"]


async def test_create_list(client: AsyncClient) -> None:
    """Create a list in a board."""
    board_id = await _create_board(client)
    resp = await client.post(
        f"/api/v1/boards/{board_id}/lists",
        json={"name": "To Do", "board_id": board_id, "position": 0},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "To Do"
    assert data["board_id"] == board_id
    assert data["position"] == 0


async def test_create_list_board_not_found(client: AsyncClient) -> None:
    """Create list in nonexistent board returns 404."""
    resp = await client.post(
        "/api/v1/boards/nonexist/lists",
        json={"name": "To Do", "board_id": "nonexist"},
    )
    assert resp.status_code == 404


async def test_create_list_validation_error(client: AsyncClient) -> None:
    """Empty name fails validation."""
    board_id = await _create_board(client)
    resp = await client.post(
        f"/api/v1/boards/{board_id}/lists",
        json={"name": "", "board_id": board_id},
    )
    assert resp.status_code == 422


async def test_list_lists(client: AsyncClient) -> None:
    """List all lists in a board."""
    board_id = await _create_board(client)
    await client.post(
        f"/api/v1/boards/{board_id}/lists",
        json={"name": "To Do", "board_id": board_id, "position": 0},
    )
    await client.post(
        f"/api/v1/boards/{board_id}/lists",
        json={"name": "Done", "board_id": board_id, "position": 1},
    )
    resp = await client.get(f"/api/v1/boards/{board_id}/lists")
    assert resp.status_code == 200
    assert len(resp.json()) == 2


async def test_list_lists_board_not_found(client: AsyncClient) -> None:
    """List lists in nonexistent board returns 404."""
    resp = await client.get("/api/v1/boards/nonexist/lists")
    assert resp.status_code == 404


async def test_list_lists_pagination(client: AsyncClient) -> None:
    """Pagination on lists."""
    board_id = await _create_board(client)
    for i in range(5):
        await client.post(
            f"/api/v1/boards/{board_id}/lists",
            json={"name": f"List {i}", "board_id": board_id, "position": i},
        )
    resp = await client.get(f"/api/v1/boards/{board_id}/lists", params={"limit": 2})
    assert len(resp.json()) == 2


async def test_get_list(client: AsyncClient) -> None:
    """Get a list by ID."""
    board_id = await _create_board(client)
    create = await client.post(
        f"/api/v1/boards/{board_id}/lists",
        json={"name": "In Progress", "board_id": board_id},
    )
    list_id = create.json()["id"]
    resp = await client.get(f"/api/v1/boards/{board_id}/lists/{list_id}")
    assert resp.status_code == 200
    assert resp.json()["name"] == "In Progress"


async def test_get_list_not_found(client: AsyncClient) -> None:
    """Get nonexistent list returns 404."""
    board_id = await _create_board(client)
    resp = await client.get(f"/api/v1/boards/{board_id}/lists/nonexist")
    assert resp.status_code == 404


async def test_get_list_wrong_board(client: AsyncClient) -> None:
    """Get list with wrong board_id returns 404."""
    board_id = await _create_board(client)
    create = await client.post(
        f"/api/v1/boards/{board_id}/lists",
        json={"name": "My List", "board_id": board_id},
    )
    list_id = create.json()["id"]
    board2_resp = await client.post("/api/v1/boards", json={"name": "Other Board"})
    board2_id = board2_resp.json()["id"]
    resp = await client.get(f"/api/v1/boards/{board2_id}/lists/{list_id}")
    assert resp.status_code == 404


async def test_update_list(client: AsyncClient) -> None:
    """Update a list."""
    board_id = await _create_board(client)
    create = await client.post(
        f"/api/v1/boards/{board_id}/lists",
        json={"name": "Old", "board_id": board_id, "position": 0},
    )
    list_id = create.json()["id"]
    resp = await client.patch(
        f"/api/v1/boards/{board_id}/lists/{list_id}",
        json={"name": "New", "position": 5},
    )
    assert resp.status_code == 200
    assert resp.json()["name"] == "New"
    assert resp.json()["position"] == 5


async def test_update_list_not_found(client: AsyncClient) -> None:
    """Update nonexistent list returns 404."""
    board_id = await _create_board(client)
    resp = await client.patch(
        f"/api/v1/boards/{board_id}/lists/nonexist", json={"name": "X"}
    )
    assert resp.status_code == 404


async def test_update_list_wrong_board(client: AsyncClient) -> None:
    """Update list with wrong board returns 404."""
    board_id = await _create_board(client)
    create = await client.post(
        f"/api/v1/boards/{board_id}/lists",
        json={"name": "My List", "board_id": board_id},
    )
    list_id = create.json()["id"]
    board2_resp = await client.post("/api/v1/boards", json={"name": "Other"})
    board2_id = board2_resp.json()["id"]
    resp = await client.patch(
        f"/api/v1/boards/{board2_id}/lists/{list_id}", json={"name": "X"}
    )
    assert resp.status_code == 404


async def test_delete_list(client: AsyncClient) -> None:
    """Delete a list."""
    board_id = await _create_board(client)
    create = await client.post(
        f"/api/v1/boards/{board_id}/lists",
        json={"name": "Delete Me", "board_id": board_id},
    )
    list_id = create.json()["id"]
    resp = await client.delete(f"/api/v1/boards/{board_id}/lists/{list_id}")
    assert resp.status_code == 204
    get_resp = await client.get(f"/api/v1/boards/{board_id}/lists/{list_id}")
    assert get_resp.status_code == 404


async def test_delete_list_not_found(client: AsyncClient) -> None:
    """Delete nonexistent list returns 404."""
    board_id = await _create_board(client)
    resp = await client.delete(f"/api/v1/boards/{board_id}/lists/nonexist")
    assert resp.status_code == 404


async def test_delete_list_wrong_board(client: AsyncClient) -> None:
    """Delete list with wrong board returns 404."""
    board_id = await _create_board(client)
    create = await client.post(
        f"/api/v1/boards/{board_id}/lists",
        json={"name": "My List", "board_id": board_id},
    )
    list_id = create.json()["id"]
    board2_resp = await client.post("/api/v1/boards", json={"name": "Other"})
    board2_id = board2_resp.json()["id"]
    resp = await client.delete(f"/api/v1/boards/{board2_id}/lists/{list_id}")
    assert resp.status_code == 404
