"""CRUD operations for boards."""

from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.db_models import BoardModel


async def create_board(db: AsyncSession, name: str, description: str = "") -> BoardModel:
    """Create a new board."""
    board = BoardModel(name=name, description=description)
    db.add(board)
    await db.commit()
    await db.refresh(board)
    return board


async def get_board(db: AsyncSession, board_id: str) -> BoardModel | None:
    """Get a board by ID."""
    return await db.get(BoardModel, board_id)


async def get_boards(
    db: AsyncSession, limit: int = 50, offset: int = 0, archived: bool | None = None
) -> list[BoardModel]:
    """Get all boards with pagination and optional filtering."""
    stmt = select(BoardModel).order_by(BoardModel.created_at.desc()).limit(limit).offset(offset)
    if archived is not None:
        stmt = stmt.where(BoardModel.archived == archived)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def update_board(
    db: AsyncSession,
    board: BoardModel,
    name: str | None = None,
    description: str | None = None,
    archived: bool | None = None,
) -> BoardModel:
    """Update a board."""
    if name is not None:
        board.name = name
    if description is not None:
        board.description = description
    if archived is not None:
        board.archived = archived
    board.updated_at = datetime.now(UTC)
    await db.commit()
    await db.refresh(board)
    return board


async def delete_board(db: AsyncSession, board: BoardModel) -> None:
    """Delete a board."""
    await db.delete(board)
    await db.commit()
