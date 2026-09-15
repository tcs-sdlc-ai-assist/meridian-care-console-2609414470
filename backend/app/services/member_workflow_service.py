"""Implement protected member-detail and care-workflow behavior."""

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.entities import AuditLog, CareGap, CarePlanGoal, Coordinator, Member, Outreach
from app.schemas.member_detail import GoalStatus


def mask_ssn(value: str) -> str:
    """Return an SSN with only its final four digits visible."""
    return f"***-**-{value[-4:]}"


def mask_mbi(value: str) -> str:
    """Return an MBI with only its final four digits visible."""
    return f"****{value[-4:]}"


async def permitted_member(session: AsyncSession, member_id: str, actor_id: str, role: str) -> Member:
    """Return a member only when the actor has the required record access."""
    member = (await session.execute(select(Member).where(Member.member_id == member_id))).scalar_one_or_none()
    if member is None or (role == "coordinator" and member.coordinator_id != actor_id):
        raise LookupError("Member not found")
    return member


async def mutable_member(session: AsyncSession, member_id: str, actor_id: str, role: str) -> Member:
    """Return a member only when the actor can mutate its workflow."""
    if role == "auditor":
        raise PermissionError("Auditors are read-only")
    return await permitted_member(session, member_id, actor_id, role)


async def member_detail(session: AsyncSession, member_id: str, actor_id: str, role: str) -> dict[str, object]:
    """Read a permitted member and its care-plan and newest-first outreach history."""
    member = await permitted_member(session, member_id, actor_id, role)
    gaps = (await session.execute(select(CareGap).where(CareGap.member_id == member_id))).scalars().all()
    goals = (await session.execute(select(CarePlanGoal).where(CarePlanGoal.member_id == member_id))).scalars().all()
    outreach = (
        await session.execute(select(Outreach).where(Outreach.member_id == member_id).order_by(Outreach.date.desc(), Outreach.id.desc()))
    ).scalars().all()
    session.add(AuditLog(actor_id=actor_id, member_id=member_id, action="member_record_opened"))
    await session.commit()
    return {
        "member_id": member.member_id,
        "name": f"{member.first_name} {member.last_name}",
        "dob": member.dob.isoformat(),
        "sex": member.sex,
        "phone": member.phone,
        "address": member.address,
        "plan": member.plan,
        "pcp": member.pcp_name,
        "risk_level": member.risk_level,
        "coordinator_id": member.coordinator_id,
        "ssn": mask_ssn(member.ssn),
        "mbi": mask_mbi(member.mbi),
        "gaps": [{"gap_id": gap.gap_id, "type": gap.type, "status": gap.status, "closed_reason": gap.closed_reason, "closed_by": gap.closed_by, "closed_at": gap.closed_at} for gap in gaps],
        "care_plan": [{"goal_id": goal.id, "text": goal.text, "status": goal.status, "updated_at": goal.updated_at} for goal in goals],
        "outreach": [{"outreach_id": item.outreach_id, "coordinator_id": item.coordinator_id, "date": item.date, "channel": item.channel, "outcome": item.outcome, "notes": item.notes} for item in outreach],
    }


async def close_gap(session: AsyncSession, member_id: str, gap_id: str, actor_id: str, role: str, reason: str) -> None:
    """Close an owned member's open care gap with attributable details."""
    await mutable_member(session, member_id, actor_id, role)
    gap = (await session.execute(select(CareGap).where(CareGap.gap_id == gap_id, CareGap.member_id == member_id))).scalar_one_or_none()
    if gap is None or gap.status != "open":
        raise LookupError("Open care gap not found")
    gap.status = "closed"
    gap.closed_reason = reason
    gap.closed_by = actor_id
    gap.closed_at = datetime.now(timezone.utc)
    await session.commit()


async def log_outreach(session: AsyncSession, member_id: str, actor_id: str, role: str, channel: str, outcome: str, notes: str) -> None:
    """Persist outreach against a member the actor is authorized to mutate."""
    await mutable_member(session, member_id, actor_id, role)
    event_time = datetime.now(timezone.utc)
    session.add(Outreach(outreach_id=f"OUT-{int(event_time.timestamp() * 1_000_000)}", member_id=member_id, coordinator_id=actor_id, channel=channel, outcome=outcome, notes=notes, date=event_time))
    await session.commit()


async def update_goal_status(session: AsyncSession, member_id: str, goal_id: int, actor_id: str, role: str, status: GoalStatus) -> None:
    """Update one owned member's care-plan goal status."""
    await mutable_member(session, member_id, actor_id, role)
    goal = (await session.execute(select(CarePlanGoal).where(CarePlanGoal.id == goal_id, CarePlanGoal.member_id == member_id))).scalar_one_or_none()
    if goal is None:
        raise LookupError("Care-plan goal not found")
    goal.status = status
    goal.updated_at = datetime.now(timezone.utc)
    await session.commit()


async def assign_member(session: AsyncSession, member_id: str, actor_id: str, role: str, coordinator_id: str) -> None:
    """Allow supervisors to assign a member to an existing coordinator."""
    if role != "supervisor":
        raise PermissionError("Only supervisors can assign members")
    member = await permitted_member(session, member_id, actor_id, role)
    coordinator = (await session.execute(select(Coordinator).where(Coordinator.coordinator_id == coordinator_id, Coordinator.role == "coordinator"))).scalar_one_or_none()
    if coordinator is None:
        raise LookupError("Coordinator not found")
    member.coordinator_id = coordinator.coordinator_id
    await session.commit()
