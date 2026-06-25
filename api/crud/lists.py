"""CRUD operations for lists."""

from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.db_models import ListModel


async def create_list(
    db: AsyncSession, name: str, board_id: str, position: int = 0
) -> ListModel:
    """Create a new list."""
    lst = ListModel(name=name, board_id=board_id, position=position)
    db.add(lst)
    await db.commit()
    await db.refresh(lst)
    return lst


async def get_list(db: AsyncSession, list_id: str) -> ListModel | None:
    """Get a list by ID."""
    return await db.get(ListModel, list_id)


async def get_lists(
    db: AsyncSession, board_id: str, limit: int = 50, offset: int = 0
) -> list[ListModel]:
    """Get all lists for a board with pagination."""
    stmt = (
        select(ListModel)
        .where(ListModel.board_id == board_id)
        .order_by(ListModel.position)
        .limit(limit)
        .offset(offset)
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def update_list(
    db: AsyncSession,
    lst: ListModel,
    name: str | None = None,
    position: int | None = None,
) -> ListModel:
    """Update a list."""
    if name is not None:
        lst.name = name
    if position is not None:
        lst.position = position
    lst.updated_at = datetime.now(UTC)
    await db.commit()
    await db.refresh(lst)
    return lst


async def delete_list(db: AsyncSession, lst: ListModel) -> None:
    """Delete a list."""
    await db.delete(lst)
    await db.commit()
