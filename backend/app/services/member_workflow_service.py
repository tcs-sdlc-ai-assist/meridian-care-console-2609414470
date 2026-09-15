"""Implement protected member-detail and care-workflow behavior."""
from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.entities import AuditLog, CareGap, Member, Outreach

def mask_ssn(value: str) -> str:
    """Return an SSN with only its final four digits visible."""
    return f'***-**-{value[-4:]}'
def mask_mbi(value: str) -> str:
    """Return an MBI with only its final four digits visible."""
    return f'****{value[-4:]}'
async def member_detail(session: AsyncSession, member_id: str, actor_id: str, role: str) -> dict:
    """Read a permitted member while recording a non-sensitive audit event."""
    member=(await session.execute(select(Member).where(Member.member_id==member_id))).scalar_one_or_none()
    if not member or (role=='coordinator' and member.coordinator_id!=actor_id): raise LookupError('Member not found')
    gaps=(await session.execute(select(CareGap).where(CareGap.member_id==member_id))).scalars().all()
    session.add(AuditLog(actor_id=actor_id,member_id=member_id,action='member_record_opened')); await session.commit()
    return {'member_id':member.member_id,'name':f'{member.first_name} {member.last_name}','dob':member.dob.isoformat(),'sex':member.sex,'phone':member.phone,'address':member.address,'plan':member.plan,'pcp':member.pcp_name,'risk_level':member.risk_level,'ssn':mask_ssn(member.ssn),'mbi':mask_mbi(member.mbi),'gaps':[{'gap_id':gap.gap_id,'type':gap.type,'status':gap.status} for gap in gaps]}
async def close_gap(session: AsyncSession, gap_id: str, actor_id: str, role: str, reason: str) -> None:
    """Close an open care gap for an authorized non-auditor."""
    if role=='auditor': raise PermissionError('Auditors are read-only')
    gap=(await session.execute(select(CareGap).where(CareGap.gap_id==gap_id))).scalar_one_or_none()
    if not gap or gap.status!='open': raise LookupError('Open care gap not found')
    gap.status='closed'; gap.closed_reason=reason; gap.closed_by=actor_id; gap.closed_at=datetime.now(timezone.utc); await session.commit()
async def log_outreach(session: AsyncSession, member_id: str, actor_id: str, role: str, channel: str, outcome: str, notes: str) -> None:
    """Persist validated outreach for an authorized staff member."""
    if role=='auditor': raise PermissionError('Auditors are read-only')
    if channel not in {'phone','SMS','mail','member portal'} or outcome not in {'reached','left message','no answer','wrong number'}: raise ValueError('Invalid outreach vocabulary')
    session.add(Outreach(outreach_id=f'OUT-{int(datetime.now().timestamp())}',member_id=member_id,coordinator_id=actor_id,channel=channel,outcome=outcome,notes=notes)); await session.commit()
