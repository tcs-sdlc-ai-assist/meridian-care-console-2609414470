"""Implement demo-login business behavior."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token, verify_password
from app.models.entities import Coordinator
from app.schemas.auth import LoginResponse, UserResponse


class InvalidCredentialsError(Exception):
    """Signal an authentication failure without revealing account existence."""


async def authenticate(email: str, password: str, session: AsyncSession) -> LoginResponse:
    """Validate staff credentials and produce an access response.

    Args:
        email: Staff email address.
        password: Submitted plaintext password.
        session: Open persistence session.

    Returns:
        Token and profile for the authenticated staff member.

    Raises:
        InvalidCredentialsError: If email/password validation fails.
    """
    result = await session.execute(select(Coordinator).where(Coordinator.email == email.lower()))
    coordinator = result.scalar_one_or_none()
    if coordinator is None or not verify_password(password, coordinator.password_hash):
        raise InvalidCredentialsError("Invalid email or password")
    return LoginResponse(
        access_token=create_access_token(coordinator.coordinator_id, coordinator.role),
        user=UserResponse.model_validate(coordinator),
    )
