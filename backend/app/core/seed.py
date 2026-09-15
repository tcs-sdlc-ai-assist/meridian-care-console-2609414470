"""Idempotently seed synthetic demonstration data."""

from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.models.entities import CareGap, Coordinator, Member


async def seed_database(session: AsyncSession) -> None:
    """Provision stable demo accounts and member records when absent.

    Args:
        session: Open database session used for idempotent inserts.
    """
    existing = await session.execute(select(Coordinator.coordinator_id).limit(1))
    if existing.scalar_one_or_none() is not None:
        return
    staff = [
        Coordinator(coordinator_id="COORD-001", name="Avery Chen", email="coordinator@meridian.example.com", password_hash=hash_password("DemoPass123!"), role="coordinator"),
        Coordinator(coordinator_id="SUP-001", name="Jordan Blake", email="supervisor@meridian.example.com", password_hash=hash_password("DemoPass123!"), role="supervisor"),
        Coordinator(coordinator_id="AUD-001", name="Morgan Reyes", email="auditor@meridian.example.com", password_hash=hash_password("DemoPass123!"), role="auditor"),
    ]
    members = [
        Member(member_id="MEM-1001", first_name="Rosa", last_name="Diaz", dob=date(1958, 4, 12), sex="Female", phone="555-0101", address="14 Cedar Way", ssn="123-45-6789", mbi="1EG4TE5MK73", plan="Meridian Gold", pcp_name="Dr. Patel", risk_level="high", coordinator_id="COORD-001"),
        Member(member_id="MEM-1002", first_name="Noah", last_name="Williams", dob=date(1964, 8, 3), sex="Male", phone="555-0102", address="29 Grove St", ssn="222-33-4444", mbi="7KT9PK2LM11", plan="Meridian Select", pcp_name="Dr. Adams", risk_level="medium", coordinator_id="COORD-001"),
    ]
    gaps = [
        CareGap(gap_id="GAP-1001", member_id="MEM-1001", type="A1c test overdue", due_date=date(2025, 1, 15), status="open"),
        CareGap(gap_id="GAP-1002", member_id="MEM-1002", type="Annual wellness visit", due_date=date(2025, 3, 1), status="open"),
    ]
    session.add_all([*staff, *members, *gaps])
    await session.commit()
