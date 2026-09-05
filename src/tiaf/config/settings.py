"""Environment-backed baseline settings."""

from pathlib import Path

from pydantic import AliasChoices, Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """General settings shared by future TIAF components."""

    model_config = SettingsConfigDict(
        env_prefix="TIAF_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    env: str = "development"
    log_level: str = "INFO"
    data_dir: Path = Path("data")
    dhan_client_id: str | None = Field(
        default=None,
        validation_alias=AliasChoices("DHAN_CLIENT_ID", "TIAF_DHAN_CLIENT_ID"),
    )
    dhan_access_token: SecretStr | None = Field(
        default=None,
        validation_alias=AliasChoices("DHAN_ACCESS_TOKEN", "TIAF_DHAN_ACCESS_TOKEN"),
    )
    dhan_base_url: str = Field(
        default="https://api.dhan.co/v2",
        validation_alias=AliasChoices("DHAN_BASE_URL", "TIAF_DHAN_BASE_URL"),
    )
