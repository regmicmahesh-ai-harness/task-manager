"""List endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from api.crud.boards import get_board
from api.crud.lists import create_list, delete_list, get_list, get_lists, update_list
from api.dependencies import get_db
from shared.schemas import ListCreate, ListResponse, ListUpdate

router = APIRouter(prefix="/boards/{board_id}/lists", tags=["lists"])


@router.post("", response_model=ListResponse, status_code=201)
async def create_list_endpoint(board_id: str, body: ListCreate, db: AsyncSession = Depends(get_db)) -> ListResponse:
    """Create a new list in a board."""
    board = await get_board(db, board_id)
    if board is None:
        raise HTTPException(status_code=404, detail="Board not found")
    lst = await create_list(db, name=body.name, board_id=board_id, position=body.position)
    return ListResponse(
        id=lst.id,
        name=lst.name,
        position=lst.position,
        board_id=lst.board_id,
        created_at=lst.created_at,
        updated_at=lst.updated_at,
    )


@router.get("", response_model=list[ListResponse])
async def list_lists_endpoint(
    board_id: str,
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
) -> list[ListResponse]:
    """List all lists in a board."""
    board = await get_board(db, board_id)
    if board is None:
        raise HTTPException(status_code=404, detail="Board not found")
    lists = await get_lists(db, board_id=board_id, limit=limit, offset=offset)
    return [
        ListResponse(
            id=lst.id,
            name=lst.name,
            position=lst.position,
            board_id=lst.board_id,
            created_at=lst.created_at,
            updated_at=lst.updated_at,
        )
        for lst in lists
    ]


@router.get("/{list_id}", response_model=ListResponse)
async def get_list_endpoint(board_id: str, list_id: str, db: AsyncSession = Depends(get_db)) -> ListResponse:
    """Get a list by ID."""
    lst = await get_list(db, list_id)
    if lst is None or lst.board_id != board_id:
        raise HTTPException(status_code=404, detail="List not found")
    return ListResponse(
        id=lst.id,
        name=lst.name,
        position=lst.position,
        board_id=lst.board_id,
        created_at=lst.created_at,
        updated_at=lst.updated_at,
    )


@router.patch("/{list_id}", response_model=ListResponse)
async def update_list_endpoint(
    board_id: str, list_id: str, body: ListUpdate, db: AsyncSession = Depends(get_db)
) -> ListResponse:
    """Update a list."""
    lst = await get_list(db, list_id)
    if lst is None or lst.board_id != board_id:
        raise HTTPException(status_code=404, detail="List not found")
    lst = await update_list(db, lst, name=body.name, position=body.position)
    return ListResponse(
        id=lst.id,
        name=lst.name,
        position=lst.position,
        board_id=lst.board_id,
        created_at=lst.created_at,
        updated_at=lst.updated_at,
    )


@router.delete("/{list_id}", status_code=204)
async def delete_list_endpoint(board_id: str, list_id: str, db: AsyncSession = Depends(get_db)) -> None:
    """Delete a list."""
    lst = await get_list(db, list_id)
    if lst is None or lst.board_id != board_id:
        raise HTTPException(status_code=404, detail="List not found")
    await delete_list(db, lst)
