"""Test seeded authentication behavior through the FastAPI HTTP surface."""

from pathlib import Path

import pytest
from httpx import ASGITransport, AsyncClient

TEST_DB = Path("/tmp/meridian-test-auth.db")


@pytest.fixture(autouse=True)
def isolate_database(monkeypatch: pytest.MonkeyPatch) -> None:
    """Point settings to a fresh file-backed SQLite database per test run."""
    TEST_DB.unlink(missing_ok=True)
    monkeypatch.setenv("DATABASE_URL", "sqlite+aiosqlite:////tmp/meridian-test-auth.db")


@pytest.mark.asyncio
async def test_seeded_coordinator_can_login() -> None:
    """Return a role-bearing token for valid seeded credentials."""
    from app.main import app

    async with app.router.lifespan_context(app):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post("/api/v1/auth/login", json={"email": "coordinator@meridian.example.com", "password": "DemoPass123!"})
    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert body["user"]["role"] == "coordinator"
    assert body["access_token"]


@pytest.mark.asyncio
async def test_login_rejects_invalid_credentials() -> None:
    """Return a non-enumerating 401 for an invalid password."""
    from app.main import app

    async with app.router.lifespan_context(app):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post("/api/v1/auth/login", json={"email": "coordinator@meridian.example.com", "password": "wrong-password"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password"


@pytest.mark.asyncio
async def test_startup_seeding_is_idempotent() -> None:
    """Allow repeated startup without duplicate seeded accounts."""
    from app.core.database import SessionLocal
    from app.main import app
    from app.models.entities import Coordinator
    from sqlalchemy import select

    async with app.router.lifespan_context(app):
        pass
    async with app.router.lifespan_context(app):
        pass
    async with SessionLocal() as session:
        result = await session.execute(select(Coordinator).where(Coordinator.email == "coordinator@meridian.example.com"))
        assert len(result.scalars().all()) == 1
