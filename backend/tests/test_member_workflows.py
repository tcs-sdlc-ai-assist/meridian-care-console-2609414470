"""Verify protected member care workflows against file-backed SQLite."""

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select


async def sign_in(client: AsyncClient, email: str) -> str:
    """Return an access token for a seeded staff account."""
    response = await client.post("/api/v1/auth/login", json={"email": email, "password": "DemoPass123!"})
    return response.json()["access_token"]


@pytest.mark.asyncio
async def test_detail_refetches_persisted_gap_closure_outreach_and_goal_status() -> None:
    """Expose persisted closure, outreach, and care-plan goal updates after refetching."""
    from app.core.database import SessionLocal, engine
    from app.main import app
    from app.models.entities import CareGap, CarePlanGoal

    assert str(engine.url).startswith("sqlite+aiosqlite:///") and ":memory:" not in str(engine.url)
    async with app.router.lifespan_context(app):
        async with SessionLocal() as session:
            gap = (await session.execute(select(CareGap).where(CareGap.gap_id == "GAP-1001"))).scalar_one()
            gap.status = "open"
            gap.closed_reason = None
            gap.closed_by = None
            gap.closed_at = None
            goal = CarePlanGoal(member_id="MEM-1001", text="Complete diabetes self-management plan", status="not-started")
            session.add(goal)
            await session.commit()
            await session.refresh(goal)
            goal_id = goal.id
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            headers = {"Authorization": f"Bearer {await sign_in(client, 'coordinator@meridian.example.com')}"}
            initial = await client.get("/api/v1/members/MEM-1001", headers=headers)
            gap_id = "GAP-1001"
            closed = await client.post(f"/api/v1/members/MEM-1001/gaps/{gap_id}/close", headers=headers, json={"reason": "Completed screening"})
            logged = await client.post("/api/v1/members/MEM-1001/outreach", headers=headers, json={"channel": "phone", "outcome": "reached", "notes": "Member confirmed appointment."})
            updated = await client.patch(f"/api/v1/members/MEM-1001/care-plan/{goal_id}", headers=headers, json={"status": "met"})
            detail = await client.get("/api/v1/members/MEM-1001", headers=headers)
    body = detail.json()
    persisted_gap = next(item for item in body["gaps"] if item["gap_id"] == gap_id)
    persisted_goal = next(item for item in body["care_plan"] if item["goal_id"] == goal_id)
    assert initial.status_code == 200 and body["ssn"] == "***-**-6789" and body["mbi"] == "****MK73"
    assert closed.status_code == 204 and logged.status_code == 201 and updated.status_code == 204
    assert persisted_gap["status"] == "closed" and persisted_gap["closed_reason"] == "Completed screening"
    assert body["outreach"][0]["notes"] == "Member confirmed appointment." and body["outreach"][0]["channel"] == "phone"
    assert persisted_goal["status"] == "met"


@pytest.mark.asyncio
async def test_mutations_reject_auditors_cross_owner_unknown_resources_and_invalid_vocabulary() -> None:
    """Enforce authorization, member ownership, 404s, and schema vocabulary validation."""
    from app.main import app

    async with app.router.lifespan_context(app):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            coordinator = {"Authorization": f"Bearer {await sign_in(client, 'coordinator@meridian.example.com')}"}
            auditor = {"Authorization": f"Bearer {await sign_in(client, 'auditor@meridian.example.com')}"}
            denied = await client.post("/api/v1/members/MEM-1001/outreach", headers=auditor, json={"channel": "phone", "outcome": "reached", "notes": "No access"})
            cross_owner = await client.post("/api/v1/members/MEM-1001/gaps/GAP-1002/close", headers=coordinator, json={"reason": "Wrong member"})
            unknown_member = await client.post("/api/v1/members/MEM-9999/outreach", headers=coordinator, json={"channel": "phone", "outcome": "reached", "notes": "Missing"})
            unknown_gap = await client.post("/api/v1/members/MEM-1001/gaps/GAP-9999/close", headers=coordinator, json={"reason": "Missing"})
            invalid = await client.post("/api/v1/members/MEM-1001/outreach", headers=coordinator, json={"channel": "email", "outcome": "reached", "notes": "Invalid"})
            invalid_goal = await client.patch("/api/v1/members/MEM-1001/care-plan/1", headers=coordinator, json={"status": "paused"})
            completed_goal = await client.patch("/api/v1/members/MEM-1001/care-plan/1", headers=coordinator, json={"status": "completed"})
    assert denied.status_code == 403 and cross_owner.status_code == 404
    assert unknown_member.status_code == 404 and unknown_gap.status_code == 404
    assert invalid.status_code == 422 and invalid_goal.status_code == 422 and completed_goal.status_code == 422
