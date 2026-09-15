"""Expose member-panel endpoints."""
from typing import Annotated
from fastapi import APIRouter, Depends, Header, HTTPException, Query
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_session
from app.core.security import decode_access_token
from app.schemas.members import MemberList
from app.services.member_service import list_members
router=APIRouter(prefix='/api/v1/members',tags=['members'])
def actor(authorization: str = Header()) -> dict[str,str]:
    """Validate bearer token."""
    try: return decode_access_token(authorization.removeprefix('Bearer '))
    except JWTError as exc: raise HTTPException(401,'Invalid token') from exc
@router.get('',response_model=MemberList)
async def get_members(claims: Annotated[dict[str,str],Depends(actor)],session: Annotated[AsyncSession,Depends(get_session)],search: str='',risk_level: str='',limit: int=Query(25,ge=1,le=100),offset: int=Query(0,ge=0)) -> MemberList:
    """List searchable members in the actor's permitted panel."""
    return await list_members(session,claims['sub'],claims['role'],search,risk_level,limit,offset)
