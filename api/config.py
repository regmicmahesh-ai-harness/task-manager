"""Application settings via pydantic-settings."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application configuration."""

    database_url: str = "sqlite+aiosqlite:///./task_manager.db"
    api_v1_prefix: str = "/api/v1"
    debug: bool = False

    model_config = {"env_prefix": "TASK_MANAGER_"}


settings = Settings()
