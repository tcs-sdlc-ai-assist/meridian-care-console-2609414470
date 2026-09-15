"""Expose authentication endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.schemas.auth import LoginRequest, LoginResponse
from app.services.auth_service import InvalidCredentialsError, authenticate

router = APIRouter(prefix="/api/v1/auth", tags=["authentication"])


@router.post("/login", response_model=LoginResponse, summary="Sign in with a seeded account")
async def login(payload: LoginRequest, session: Annotated[AsyncSession, Depends(get_session)]) -> LoginResponse:
    """Authenticate a staff member with seeded demo credentials.

    Args:
        payload: Email and password supplied by the login form.
        session: Request-scoped database session.

    Returns:
        JWT access token and safe staff profile.

    Raises:
        HTTPException: If the submitted credentials are invalid.
    """
    try:
        return await authenticate(str(payload.email), payload.password, session)
    except InvalidCredentialsError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password") from exc
