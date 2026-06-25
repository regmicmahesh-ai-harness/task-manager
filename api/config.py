"""Application settings via pydantic-settings."""

import os
from pathlib import Path

from pydantic_settings import BaseSettings

DATA_DIR = Path(os.environ.get("TASK_MANAGER_DATA_DIR", Path.home() / ".local" / "share" / "task-manager"))
DATA_DIR.mkdir(parents=True, exist_ok=True)

DEFAULT_DB_URL = f"sqlite+aiosqlite:///{DATA_DIR / 'task_manager.db'}"


class Settings(BaseSettings):
    """Application configuration."""

    database_url: str = DEFAULT_DB_URL
    api_v1_prefix: str = "/api/v1"
    debug: bool = False

    model_config = {"env_prefix": "TASK_MANAGER_"}


settings = Settings()
