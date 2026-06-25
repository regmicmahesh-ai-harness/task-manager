"""Card endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from api.crud.cards import (
    bulk_move_cards,
    create_card,
    delete_card,
    get_card,
    get_cards,
    move_card,
    update_card,
)
from api.crud.lists import get_list
from api.dependencies import get_db
from shared.schemas import BulkCardMove, CardCreate, CardMove, CardResponse, CardUpdate

router = APIRouter(prefix="/cards", tags=["cards"])


def _card_to_response(card: object) -> CardResponse:
    """Convert a CardModel to CardResponse."""
    from api.db_models import CardModel

    assert isinstance(card, CardModel)
    labels = [lb.strip() for lb in card.labels.split(",") if lb.strip()] if card.labels else []
    return CardResponse(
        id=card.id,
        title=card.title,
        description=card.description,
        position=card.position,
        list_id=card.list_id,
        priority=card.priority,
        labels=labels,
        due_date=card.due_date,
        created_at=card.created_at,
        updated_at=card.updated_at,
    )


@router.post("", response_model=CardResponse, status_code=201)
async def create_card_endpoint(body: CardCreate, db: AsyncSession = Depends(get_db)) -> CardResponse:
    """Create a new card."""
    lst = await get_list(db, body.list_id)
    if lst is None:
        raise HTTPException(status_code=404, detail="List not found")
    labels_str = ",".join(body.labels) if body.labels else ""
    card = await create_card(
        db,
        title=body.title,
        list_id=body.list_id,
        description=body.description,
        position=body.position,
        priority=body.priority.value,
        labels=labels_str,
        due_date=body.due_date,
    )
    return _card_to_response(card)


@router.get("", response_model=list[CardResponse])
async def list_cards_endpoint(
    list_id: str | None = None,
    priority: str | None = None,
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
) -> list[CardResponse]:
    """List cards with optional filtering."""
    cards = await get_cards(db, list_id=list_id, priority=priority, limit=limit, offset=offset)
    return [_card_to_response(c) for c in cards]


@router.get("/{card_id}", response_model=CardResponse)
async def get_card_endpoint(card_id: str, db: AsyncSession = Depends(get_db)) -> CardResponse:
    """Get a card by ID."""
    card = await get_card(db, card_id)
    if card is None:
        raise HTTPException(status_code=404, detail="Card not found")
    return _card_to_response(card)


@router.patch("/{card_id}", response_model=CardResponse)
async def update_card_endpoint(card_id: str, body: CardUpdate, db: AsyncSession = Depends(get_db)) -> CardResponse:
    """Update a card."""
    card = await get_card(db, card_id)
    if card is None:
        raise HTTPException(status_code=404, detail="Card not found")
    labels_str = ",".join(body.labels) if body.labels is not None else None
    kwargs: dict[str, object] = {}
    if body.title is not None:
        kwargs["title"] = body.title
    if body.description is not None:
        kwargs["description"] = body.description
    if body.position is not None:
        kwargs["position"] = body.position
    if body.priority is not None:
        kwargs["priority"] = body.priority.value
    if labels_str is not None:
        kwargs["labels"] = labels_str
    kwargs["due_date"] = body.due_date
    card = await update_card(db, card, **kwargs)  # type: ignore[arg-type]
    return _card_to_response(card)


@router.post("/{card_id}/move", response_model=CardResponse)
async def move_card_endpoint(card_id: str, body: CardMove, db: AsyncSession = Depends(get_db)) -> CardResponse:
    """Move a card to a different list."""
    card = await get_card(db, card_id)
    if card is None:
        raise HTTPException(status_code=404, detail="Card not found")
    target_list = await get_list(db, body.to_list_id)
    if target_list is None:
        raise HTTPException(status_code=404, detail="Target list not found")
    card = await move_card(db, card, to_list_id=body.to_list_id, position=body.position)
    return _card_to_response(card)


@router.post("/bulk", response_model=list[CardResponse])
async def bulk_move_cards_endpoint(body: BulkCardMove, db: AsyncSession = Depends(get_db)) -> list[CardResponse]:
    """Move multiple cards to a different list."""
    target_list = await get_list(db, body.to_list_id)
    if target_list is None:
        raise HTTPException(status_code=404, detail="Target list not found")
    cards = await bulk_move_cards(db, card_ids=body.card_ids, to_list_id=body.to_list_id)
    return [_card_to_response(c) for c in cards]


@router.delete("/{card_id}", status_code=204)
async def delete_card_endpoint(card_id: str, db: AsyncSession = Depends(get_db)) -> None:
    """Delete a card."""
    card = await get_card(db, card_id)
    if card is None:
        raise HTTPException(status_code=404, detail="Card not found")
    await delete_card(db, card)
