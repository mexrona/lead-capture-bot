from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    bot_token: str = Field(..., alias="BOT_TOKEN")
    manager_chat_id: int = Field(..., alias="MANAGER_CHAT_ID")

    google_sheets_credentials_path: str = Field(
        "credentials/google-service-account.json",
        alias="GOOGLE_SHEETS_CREDENTIALS_PATH",
    )
    google_sheets_spreadsheet_id: str = Field(..., alias="GOOGLE_SHEETS_SPREADSHEET_ID")
    google_sheets_worksheet_name: str = Field("Leads", alias="GOOGLE_SHEETS_WORKSHEET_NAME")

    lead_storage_backend: Literal["google_sheets"] = Field(
        "google_sheets",
        alias="LEAD_STORAGE_BACKEND",
    )

    fsm_storage: Literal["memory", "sqlite", "postgresql"] = Field(
        "sqlite",
        alias="FSM_STORAGE",
    )
    fsm_sqlite_path: str = Field("data/fsm.db", alias="FSM_SQLITE_PATH")
    postgres_dsn: str = Field(
        "postgresql+asyncpg://leadbot:leadbot@localhost:5432/leadbot",
        alias="POSTGRES_DSN",
    )

    draft_timeout_hours: int = Field(24, alias="DRAFT_TIMEOUT_HOURS")
    reminder_minutes: int = Field(15, alias="REMINDER_MINUTES")
    log_level: str = Field("INFO", alias="LOG_LEVEL")

    nlp_enabled: bool = Field(False, alias="NLP_ENABLED")

    manager_contact_name: str = Field("Менеджер", alias="MANAGER_CONTACT_NAME")
    manager_contact_phone: str = Field("", alias="MANAGER_CONTACT_PHONE")
    manager_contact_telegram: str = Field("", alias="MANAGER_CONTACT_TELEGRAM")


@lru_cache
def get_settings() -> Settings:
    return Settings()
