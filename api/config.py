"""Application settings via pydantic-settings."""

from pydantic_settings import BaseSettings

from shared.socket import API_PREFIX, DATA_DIR, PID_PATH, SOCKET_PATH

DEFAULT_DB_URL = f"sqlite+aiosqlite:///{DATA_DIR / 'task_manager.db'}"


class Settings(BaseSettings):
    """Application configuration."""

    database_url: str = DEFAULT_DB_URL
    api_v1_prefix: str = API_PREFIX
    socket_path: str = SOCKET_PATH
    pid_path: str = PID_PATH
    debug: bool = False

    model_config = {"env_prefix": "TASK_MANAGER_"}


settings = Settings()
