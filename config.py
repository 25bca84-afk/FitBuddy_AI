from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    app_name: str = Field(
        default="FitBuddy",
        validation_alias="APP_NAME"
    )

    app_version: str = Field(
        default="1.0.0",
        validation_alias="APP_VERSION"
    )

    debug: bool = Field(
        default=True,
        validation_alias="DEBUG"
    )

    database_url: str = Field(
        default="sqlite:///./fitbuddy.db",
        validation_alias="DATABASE_URL"
    )

    gemini_api_key: str = Field(
        default="",
        validation_alias="GEMINI_API_KEY"
    )

    workout_model: str = Field(
        default="gemini-2.5-flash",
        validation_alias="GEMINI_WORKOUT_MODEL"
    )

    tip_model: str = Field(
        default="gemini-2.5-flash",
        validation_alias="GEMINI_TIP_MODEL"
    )

    admin_key: str = Field(
        default="fitbuddy-admin-123",
        validation_alias="ADMIN_KEY"
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()