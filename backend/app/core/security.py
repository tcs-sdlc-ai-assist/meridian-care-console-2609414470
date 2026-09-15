"""Provide password and JSON Web Token security helpers."""

from datetime import datetime, timedelta, timezone

import bcrypt
from jose import JWTError, jwt

from app.core.config import settings


def hash_password(password: str) -> str:
    """Hash a password with bcrypt.

    Args:
        password: Plaintext password supplied during account provisioning.

    Returns:
        A bcrypt hash suitable for persistent storage.
    """
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, password_hash: str) -> bool:
    """Verify supplied credentials against a stored hash.

    Args:
        password: Candidate plaintext password.
        password_hash: Persisted bcrypt hash.

    Returns:
        Whether the credentials match.
    """
    return bcrypt.checkpw(password.encode(), password_hash.encode())


def create_access_token(subject: str, role: str) -> str:
    """Issue a signed role-bearing access token.

    Args:
        subject: Stable coordinator business identifier.
        role: Authorized application role.

    Returns:
        Signed JWT with expiration.
    """
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_expire_minutes)
    return jwt.encode({"sub": subject, "role": role, "exp": expires_at}, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> dict[str, str]:
    """Decode and validate an access token.

    Args:
        token: JWT supplied by the client.

    Returns:
        Token claims containing subject and role.

    Raises:
        JWTError: If signature or expiration validation fails.
    """
    return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
