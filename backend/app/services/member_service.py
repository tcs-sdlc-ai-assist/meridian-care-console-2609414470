"""Implement scoped member-panel queries."""
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.entities import CareGap, Member
from app.schemas.members import MemberList, MemberRow
async def list_members(session: AsyncSession, actor_id: str, role: str, search: str = '', risk_level: str = '', limit: int = 25, offset: int = 0) -> MemberList:
    """Return a bounded, role-scoped member panel."""
    statement = select(Member).order_by(Member.last_name).offset(offset).limit(limit)
    if role == 'coordinator': statement = statement.where(Member.coordinator_id == actor_id)
    if search: statement = statement.where((Member.first_name + ' ' + Member.last_name).ilike(f'%{search}%'))
    if risk_level: statement = statement.where(Member.risk_level == risk_level)
    members = (await session.execute(statement)).scalars().all()
    rows=[]
    for member in members:
        open_gaps=(await session.execute(select(func.count(CareGap.id)).where(CareGap.member_id==member.member_id, CareGap.status=='open'))).scalar_one()
        rows.append(MemberRow(member_id=member.member_id,name=f'{member.first_name} {member.last_name}',dob=member.dob.isoformat(),plan=member.plan,pcp=member.pcp_name,risk_level=member.risk_level,open_gaps=open_gaps,coordinator_id=member.coordinator_id))
    return MemberList(items=rows,total=len(rows))
