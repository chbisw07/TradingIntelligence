"""Secret-safe configuration for the Dhan data adapter."""

from typing import Self

from pydantic import AnyHttpUrl, BaseModel, ConfigDict, Field, SecretStr, field_validator

from tiaf.config import Settings
from tiaf.data import ProviderAuthError


class DhanConfig(BaseModel):
    """Credentials and transport settings required by DhanHQ v2 data APIs."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    client_id: str = Field(min_length=1)
    access_token: SecretStr
    base_url: AnyHttpUrl = AnyHttpUrl("https://api.dhan.co/v2")
    timeout_seconds: float = Field(default=10.0, gt=0)

    @field_validator("client_id")
    @classmethod
    def strip_client_id(cls, value: str) -> str:
        """Reject empty client identifiers after trimming."""
        normalized = value.strip()
        if not normalized:
            raise ValueError("client_id must not be empty")
        return normalized

    @field_validator("access_token")
    @classmethod
    def require_access_token(cls, value: SecretStr) -> SecretStr:
        """Reject empty access tokens without exposing their value."""
        if not value.get_secret_value().strip():
            raise ValueError("access_token must not be empty")
        return value

    @classmethod
    def from_settings(cls, settings: Settings) -> Self:
        """Build config from application settings or raise a typed auth error."""
        if settings.dhan_client_id is None or settings.dhan_access_token is None:
            raise ProviderAuthError(
                "Dhan credentials are required",
                provider="DHAN",
            )
        return cls.model_validate(
            {
                "client_id": settings.dhan_client_id,
                "access_token": settings.dhan_access_token,
                "base_url": settings.dhan_base_url,
            }
        )
