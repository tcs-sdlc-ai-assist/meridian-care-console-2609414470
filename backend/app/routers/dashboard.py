"""Expose dashboard endpoints."""
from typing import Annotated
from fastapi import APIRouter, Depends, Header, HTTPException
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_session
from app.core.security import decode_access_token
from app.schemas.dashboard import DashboardResponse
from app.services.dashboard_service import dashboard
router=APIRouter(prefix='/api/v1/dashboard',tags=['dashboard'])
def actor(authorization: str = Header()) -> dict[str,str]:
    """Validate bearer token and return claims."""
    try: return decode_access_token(authorization.removeprefix('Bearer '))
    except JWTError as exc: raise HTTPException(401,'Invalid token') from exc
@router.get('',response_model=DashboardResponse)
async def get_dashboard(claims: Annotated[dict[str,str],Depends(actor)], session: Annotated[AsyncSession,Depends(get_session)]) -> DashboardResponse:
    """Return role-scoped dashboard data."""
    return await dashboard(session,claims['sub'],claims['role'])
