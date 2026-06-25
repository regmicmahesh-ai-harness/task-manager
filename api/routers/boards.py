"""Board endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from api.crud.boards import (
    create_board,
    delete_board,
    get_board,
    get_boards,
    update_board,
)
from api.dependencies import get_db
from shared.schemas import BoardCreate, BoardResponse, BoardUpdate

router = APIRouter(prefix="/boards", tags=["boards"])


@router.post("", response_model=BoardResponse, status_code=201)
async def create_board_endpoint(body: BoardCreate, db: AsyncSession = Depends(get_db)) -> BoardResponse:
    """Create a new board."""
    board = await create_board(db, name=body.name, description=body.description)
    return BoardResponse(
        id=board.id,
        name=board.name,
        description=board.description,
        archived=board.archived,
        created_at=board.created_at,
        updated_at=board.updated_at,
    )


@router.get("", response_model=list[BoardResponse])
async def list_boards_endpoint(
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    archived: bool | None = None,
    db: AsyncSession = Depends(get_db),
) -> list[BoardResponse]:
    """List all boards."""
    boards = await get_boards(db, limit=limit, offset=offset, archived=archived)
    return [
        BoardResponse(
            id=b.id,
            name=b.name,
            description=b.description,
            archived=b.archived,
            created_at=b.created_at,
            updated_at=b.updated_at,
        )
        for b in boards
    ]


@router.get("/{board_id}", response_model=BoardResponse)
async def get_board_endpoint(board_id: str, db: AsyncSession = Depends(get_db)) -> BoardResponse:
    """Get a board by ID."""
    board = await get_board(db, board_id)
    if board is None:
        raise HTTPException(status_code=404, detail="Board not found")
    return BoardResponse(
        id=board.id,
        name=board.name,
        description=board.description,
        archived=board.archived,
        created_at=board.created_at,
        updated_at=board.updated_at,
    )


@router.patch("/{board_id}", response_model=BoardResponse)
async def update_board_endpoint(board_id: str, body: BoardUpdate, db: AsyncSession = Depends(get_db)) -> BoardResponse:
    """Update a board."""
    board = await get_board(db, board_id)
    if board is None:
        raise HTTPException(status_code=404, detail="Board not found")
    board = await update_board(db, board, name=body.name, description=body.description, archived=body.archived)
    return BoardResponse(
        id=board.id,
        name=board.name,
        description=board.description,
        archived=board.archived,
        created_at=board.created_at,
        updated_at=board.updated_at,
    )


@router.delete("/{board_id}", status_code=204)
async def delete_board_endpoint(board_id: str, db: AsyncSession = Depends(get_db)) -> None:
    """Delete a board."""
    board = await get_board(db, board_id)
    if board is None:
        raise HTTPException(status_code=404, detail="Board not found")
    await delete_board(db, board)
