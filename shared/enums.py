"""Shared enums for the task manager."""

from enum import StrEnum


class CardStatus(StrEnum):
    """Status of a card."""

    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    ARCHIVED = "archived"


class CardPriority(StrEnum):
    """Priority level of a card."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"
