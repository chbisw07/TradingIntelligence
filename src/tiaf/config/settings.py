"""Environment-backed baseline settings."""

from pathlib import Path

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
