"""Expose protected member-detail care workflows."""
from typing import Annotated
from fastapi import APIRouter, Depends, Header, HTTPException
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_session
from app.core.security import decode_access_token
from app.schemas.member_detail import GapCloseRequest, MemberDetail, OutreachRequest
from app.services.member_workflow_service import close_gap, log_outreach, member_detail
router=APIRouter(prefix='/api/v1/members',tags=['member workflows'])
def actor(authorization: str=Header()) -> dict[str,str]:
    """Decode the required bearer token."""
    try:return decode_access_token(authorization.removeprefix('Bearer '))
    except JWTError as exc: raise HTTPException(401,'Invalid token') from exc
@router.get('/{member_id}',response_model=MemberDetail)
async def detail(member_id:str,claims:Annotated[dict[str,str],Depends(actor)],session:Annotated[AsyncSession,Depends(get_session)]) -> dict:
    """Return a masked, audited member detail."""
    try:return await member_detail(session,member_id,claims['sub'],claims['role'])
    except LookupError as exc:raise HTTPException(404,str(exc)) from exc
@router.post('/{member_id}/gaps/{gap_id}/close',status_code=204)
async def close(member_id:str,gap_id:str,payload:GapCloseRequest,claims:Annotated[dict[str,str],Depends(actor)],session:Annotated[AsyncSession,Depends(get_session)]) -> None:
    """Close a care gap with an attributable reason."""
    try: await close_gap(session,gap_id,claims['sub'],claims['role'],payload.reason)
    except PermissionError as exc:raise HTTPException(403,str(exc)) from exc
    except LookupError as exc:raise HTTPException(404,str(exc)) from exc
@router.post('/{member_id}/outreach',status_code=201)
async def outreach(member_id:str,payload:OutreachRequest,claims:Annotated[dict[str,str],Depends(actor)],session:Annotated[AsyncSession,Depends(get_session)]) -> None:
    """Log an outreach attempt."""
    try:await log_outreach(session,member_id,claims['sub'],claims['role'],payload.channel,payload.outcome,payload.notes)
    except PermissionError as exc:raise HTTPException(403,str(exc)) from exc
    except ValueError as exc:raise HTTPException(422,str(exc)) from exc
