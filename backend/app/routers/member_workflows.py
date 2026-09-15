"""Expose protected member-detail care workflows."""

from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, status
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.core.security import decode_access_token
from app.schemas.member_detail import AssignmentRequest, GapCloseRequest, GoalUpdateRequest, MemberDetail, OutreachRequest
from app.services.member_workflow_service import assign_member, close_gap, log_outreach, member_detail, update_goal_status

router = APIRouter(prefix="/api/v1/members", tags=["member workflows"])


def actor(authorization: str = Header()) -> dict[str, str]:
    """Decode the required bearer token."""
    try:
        return decode_access_token(authorization.removeprefix("Bearer "))
    except JWTError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from exc


@router.get("/{member_id}", response_model=MemberDetail, status_code=status.HTTP_200_OK)
async def detail(member_id: str, claims: Annotated[dict[str, str], Depends(actor)], session: Annotated[AsyncSession, Depends(get_session)]) -> dict[str, object]:
    """Return a masked, audited member detail and workflow read model."""
    try:
        return await member_detail(session, member_id, claims["sub"], claims["role"])
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.post("/{member_id}/gaps/{gap_id}/close", status_code=status.HTTP_204_NO_CONTENT)
async def close(member_id: str, gap_id: str, payload: GapCloseRequest, claims: Annotated[dict[str, str], Depends(actor)], session: Annotated[AsyncSession, Depends(get_session)]) -> None:
    """Close an authorized member's care gap with an attributable reason."""
    try:
        await close_gap(session, member_id, gap_id, claims["sub"], claims["role"], payload.reason)
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.post("/{member_id}/outreach", status_code=status.HTTP_201_CREATED)
async def outreach(member_id: str, payload: OutreachRequest, claims: Annotated[dict[str, str], Depends(actor)], session: Annotated[AsyncSession, Depends(get_session)]) -> None:
    """Log an authorized member outreach attempt."""
    try:
        await log_outreach(session, member_id, claims["sub"], claims["role"], payload.channel, payload.outcome, payload.notes)
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.patch("/{member_id}/care-plan/{goal_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_goal(member_id: str, goal_id: int, payload: GoalUpdateRequest, claims: Annotated[dict[str, str], Depends(actor)], session: Annotated[AsyncSession, Depends(get_session)]) -> None:
    """Update an authorized member's care-plan goal status."""
    try:
        await update_goal_status(session, member_id, goal_id, claims["sub"], claims["role"], payload.status)
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.patch("/{member_id}/assignment", status_code=status.HTTP_204_NO_CONTENT)
async def assign(member_id: str, payload: AssignmentRequest, claims: Annotated[dict[str, str], Depends(actor)], session: Annotated[AsyncSession, Depends(get_session)]) -> None:
    """Allow a supervisor to assign a member to a coordinator."""
    try:
        await assign_member(session, member_id, claims["sub"], claims["role"], payload.coordinator_id)
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
