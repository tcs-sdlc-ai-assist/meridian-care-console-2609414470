"""Define authentication request and response contracts."""

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class LoginRequest(BaseModel):
    """Accept staff credentials for a demo login."""

    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class UserResponse(BaseModel):
    """Expose safe authenticated staff information."""

    coordinator_id: str
    name: str
    email: EmailStr
    role: str

    model_config = ConfigDict(from_attributes=True)


class LoginResponse(BaseModel):
    """Return an access token and safe staff profile."""

    access_token: str
    token_type: str = "bearer"
    user: UserResponse
