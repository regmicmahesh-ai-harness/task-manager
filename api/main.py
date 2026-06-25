"""FastAPI application factory."""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator

from fastapi import FastAPI

from api.config import settings
from api.database import engine
from api.db_models import Base
from api.routers import boards, cards, health, lists


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    """Create tables on startup."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(title="Task Manager", version="0.1.0", lifespan=lifespan)

app.include_router(health.router, prefix=settings.api_v1_prefix)
app.include_router(boards.router, prefix=settings.api_v1_prefix)
app.include_router(lists.router, prefix=settings.api_v1_prefix)
app.include_router(cards.router, prefix=settings.api_v1_prefix)


def serve() -> None:  # pragma: no cover
    """Start the API server on a Unix domain socket."""
    import os

    import uvicorn

    sock = settings.socket_path
    pid_path = settings.pid_path
    # Remove stale socket file if it exists.
    if os.path.exists(sock):
        os.unlink(sock)
    # Write PID file so other processes can detect a running server.
    with open(pid_path, "w") as f:
        f.write(str(os.getpid()))
    try:
        uvicorn.run("api.main:app", uds=sock, log_level="info")
    finally:
        # Clean up PID and socket on shutdown.
        if os.path.exists(pid_path):
            os.unlink(pid_path)
        if os.path.exists(sock):
            os.unlink(sock)
