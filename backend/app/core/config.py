"""Load application settings from environment variables."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Provide typed runtime configuration for the API."""

    database_url: str = "sqlite+aiosqlite:////tmp/meridian/app.db"
    jwt_secret: str = "dev-secret-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 480
    seed_on_startup: bool = True
    cors_origins: str = "http://localhost:5173"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def cors_origin_list(self) -> list[str]:
        """Split configured browser origins into an allow list.

        Returns:
            Explicit development origins accepted by CORS middleware.
        """
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


settings = Settings()
