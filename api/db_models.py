"""SQLAlchemy ORM models."""

import uuid
from datetime import UTC, datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


def _generate_short_id() -> str:
    """Generate an 8-char short UUID."""
    return uuid.uuid4().hex[:8]


def _utcnow() -> datetime:
    """Return current UTC datetime."""
    return datetime.now(UTC)


class Base(DeclarativeBase):
    """Base class for all ORM models."""

    pass


class BoardModel(Base):
    """Board ORM model."""

    __tablename__ = "boards"

    id: Mapped[str] = mapped_column(String(8), primary_key=True, default=_generate_short_id)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="")
    archived: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow, onupdate=_utcnow)

    lists: Mapped[list["ListModel"]] = relationship(
        back_populates="board", cascade="all, delete-orphan"
    )


class ListModel(Base):
    """List ORM model."""

    __tablename__ = "lists"

    id: Mapped[str] = mapped_column(String(8), primary_key=True, default=_generate_short_id)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    position: Mapped[int] = mapped_column(Integer, default=0)
    board_id: Mapped[str] = mapped_column(
        String(8), ForeignKey("boards.id", ondelete="CASCADE"), nullable=False, index=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow, onupdate=_utcnow)

    board: Mapped["BoardModel"] = relationship(back_populates="lists")
    cards: Mapped[list["CardModel"]] = relationship(
        back_populates="list_", cascade="all, delete-orphan"
    )


class CardModel(Base):
    """Card ORM model."""

    __tablename__ = "cards"

    id: Mapped[str] = mapped_column(String(8), primary_key=True, default=_generate_short_id)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="")
    position: Mapped[int] = mapped_column(Integer, default=0)
    list_id: Mapped[str] = mapped_column(
        String(8), ForeignKey("lists.id", ondelete="CASCADE"), nullable=False, index=True
    )
    priority: Mapped[str] = mapped_column(String(10), default="medium")
    status: Mapped[str] = mapped_column(String(15), default="todo")
    labels: Mapped[str] = mapped_column(Text, default="")  # comma-separated
    due_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow, onupdate=_utcnow)

    list_: Mapped["ListModel"] = relationship(back_populates="cards")


class LabelModel(Base):
    """Label ORM model."""

    __tablename__ = "labels"

    id: Mapped[str] = mapped_column(String(8), primary_key=True, default=_generate_short_id)
    name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    color: Mapped[str] = mapped_column(String(7), default="#808080")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow, onupdate=_utcnow)
