"""Create and configure the Meridian Care Console API."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import SessionLocal, create_tables
from app.core.seed import seed_database
from app.routers.auth import router as auth_router


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Initialize the SQLite schema and optional demo data.

    Yields:
        Control to the active FastAPI application.
    """
    await create_tables()
    if settings.seed_on_startup:
        async with SessionLocal() as session:
            await seed_database(session)
    yield


app = FastAPI(title="Meridian Care Console API", version="1.0.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origin_list, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.include_router(auth_router)


@app.get("/api/health", tags=["health"], summary="Return process liveness")
async def health() -> dict[str, str]:
    """Report that the FastAPI process is available.

    Returns:
        A small dependency-free liveness payload.
    """
    return {"status": "ok"}
