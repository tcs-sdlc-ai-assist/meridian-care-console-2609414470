"""Implement role-aware operational dashboard metrics."""
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.entities import CareGap, Member
from app.schemas.dashboard import DashboardResponse, Metric
async def dashboard(session: AsyncSession, actor_id: str, role: str) -> DashboardResponse:
    """Summarize current operational workload for the requesting role."""
    members=select(Member)
    if role=='coordinator': members=members.where(Member.coordinator_id==actor_id)
    rows=(await session.execute(members)).scalars().all(); ids=[row.member_id for row in rows]
    gaps=0 if not ids else (await session.execute(select(func.count(CareGap.id)).where(CareGap.member_id.in_(ids),CareGap.status=='open'))).scalar_one()
    high=[f'{row.first_name} {row.last_name}' for row in rows if row.risk_level=='high']
    return DashboardResponse(metrics=[Metric(label='Members assigned',value=len(rows)),Metric(label='Open care gaps',value=gaps),Metric(label='High-risk members',value=len(high)),Metric(label='Gap-closure rate',value=0)],attention=high,activity=['Demo environment seeded'],chart=[gaps, len(high), max(gaps-len(high),0)])
