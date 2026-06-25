"""FastAPI application factory."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from api.config import settings
from api.database import engine
from api.db_models import Base
from api.routers import boards, cards, health, lists


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Create tables on startup."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(title="Task Manager", version="0.1.0", lifespan=lifespan)

app.include_router(health.router, prefix=settings.api_v1_prefix)
app.include_router(boards.router, prefix=settings.api_v1_prefix)
app.include_router(lists.router, prefix=settings.api_v1_prefix)
app.include_router(cards.router, prefix=settings.api_v1_prefix)
