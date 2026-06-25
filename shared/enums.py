"""Shared enums for the task manager."""

from enum import StrEnum


class CardPriority(StrEnum):
    """Priority level of a card."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


# Default columns created for every new board.
DEFAULT_COLUMNS = ["To Do", "In Progress", "Done"]
