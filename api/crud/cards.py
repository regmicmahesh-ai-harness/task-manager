"""CRUD operations for cards."""

from datetime import UTC, datetime
from enum import Enum, auto

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.db_models import CardModel


class _Unset(Enum):
    """Sentinel for distinguishing 'not provided' from None."""

    UNSET = auto()


async def create_card(
    db: AsyncSession,
    title: str,
    list_id: str,
    description: str = "",
    position: int = 0,
    priority: str = "medium",
    labels: str = "",
    due_date: datetime | None = None,
) -> CardModel:
    """Create a new card."""
    card = CardModel(
        title=title,
        list_id=list_id,
        description=description,
        position=position,
        priority=priority,
        labels=labels,
        due_date=due_date,
    )
    db.add(card)
    await db.commit()
    await db.refresh(card)
    return card


async def get_card(db: AsyncSession, card_id: str) -> CardModel | None:
    """Get a card by ID."""
    return await db.get(CardModel, card_id)


async def get_cards(
    db: AsyncSession,
    list_id: str | None = None,
    priority: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> list[CardModel]:
    """Get cards with optional filtering and pagination."""
    stmt = select(CardModel).order_by(CardModel.position).limit(limit).offset(offset)
    if list_id is not None:
        stmt = stmt.where(CardModel.list_id == list_id)
    if priority is not None:
        stmt = stmt.where(CardModel.priority == priority)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def update_card(
    db: AsyncSession,
    card: CardModel,
    title: str | None = None,
    description: str | None = None,
    position: int | None = None,
    priority: str | None = None,
    labels: str | None = None,
    due_date: datetime | None | _Unset = _Unset.UNSET,
) -> CardModel:
    """Update a card."""
    if title is not None:
        card.title = title
    if description is not None:
        card.description = description
    if position is not None:
        card.position = position
    if priority is not None:
        card.priority = priority
    if labels is not None:
        card.labels = labels
    if not isinstance(due_date, _Unset):
        card.due_date = due_date
    card.updated_at = datetime.now(UTC)
    await db.commit()
    await db.refresh(card)
    return card


async def move_card(db: AsyncSession, card: CardModel, to_list_id: str, position: int = 0) -> CardModel:
    """Move a card to a different list."""
    card.list_id = to_list_id
    card.position = position
    card.updated_at = datetime.now(UTC)
    await db.commit()
    await db.refresh(card)
    return card


async def bulk_move_cards(db: AsyncSession, card_ids: list[str], to_list_id: str) -> list[CardModel]:
    """Move multiple cards to a different list."""
    stmt = select(CardModel).where(CardModel.id.in_(card_ids))
    result = await db.execute(stmt)
    cards = list(result.scalars().all())
    now = datetime.now(UTC)
    for card in cards:
        card.list_id = to_list_id
        card.updated_at = now
    await db.commit()
    for card in cards:
        await db.refresh(card)
    return cards


async def delete_card(db: AsyncSession, card: CardModel) -> None:
    """Delete a card."""
    await db.delete(card)
    await db.commit()
