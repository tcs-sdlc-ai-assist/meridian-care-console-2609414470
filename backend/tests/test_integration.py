"""Exercise cross-feature persisted member-care journeys."""

import pytest
from httpx import ASGITransport, AsyncClient


async def sign_in(client: AsyncClient, email: str) -> str:
    """Return a seeded account token."""
    response = await client.post("/api/v1/auth/login", json={"email": email, "password": "DemoPass123!"})
    return response.json()["access_token"]


@pytest.mark.asyncio
async def test_login_dashboard_member_detail_closure_and_supervisor_assignment_chain() -> None:
    """Carry identities through dashboard, member workflows, and persisted reassignment."""
    from app.main import app

    async with app.router.lifespan_context(app):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            coordinator_headers = {"Authorization": f"Bearer {await sign_in(client, 'coordinator@meridian.example.com')}"}
            supervisor_headers = {"Authorization": f"Bearer {await sign_in(client, 'supervisor@meridian.example.com')}"}
            dashboard = await client.get("/api/v1/dashboard", headers=coordinator_headers)
            detail = await client.get("/api/v1/members/MEM-1001", headers=coordinator_headers)
            reassigned = await client.patch("/api/v1/members/MEM-1001/assignment", headers=supervisor_headers, json={"coordinator_id": "COORD-001"})
            refetched = await client.get("/api/v1/members/MEM-1001", headers=supervisor_headers)
    assert dashboard.status_code == 200 and detail.status_code == 200
    assert detail.json()["ssn"] == "***-**-6789"
    assert reassigned.status_code == 204 and refetched.json()["coordinator_id"] == "COORD-001"
