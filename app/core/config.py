from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = Field(default="OmniFlow Business Sync Demo", alias="APP_NAME")
    app_env: str = Field(default="local", alias="APP_ENV")
    app_host: str = Field(default="0.0.0.0", alias="APP_HOST")
    app_port: int = Field(default=8000, alias="APP_PORT")

    database_path: str = Field(default="./data/omniflow.db", alias="DATABASE_PATH")
    default_provider: str = Field(default="mock", alias="DEFAULT_PROVIDER")
    provider_fallback_order: str = Field(default="mock,openai,anthropic,gemini", alias="PROVIDER_FALLBACK_ORDER")

    request_timeout_seconds: int = Field(default=20, alias="REQUEST_TIMEOUT_SECONDS")
    max_retries: int = Field(default=2, alias="MAX_RETRIES")

    enable_connectors: bool = Field(default=False, alias="ENABLE_CONNECTORS")
    enable_github_connector: bool = Field(default=False, alias="ENABLE_GITHUB_CONNECTOR")
    enable_slack_connector: bool = Field(default=False, alias="ENABLE_SLACK_CONNECTOR")
    enable_sheets_connector: bool = Field(default=False, alias="ENABLE_SHEETS_CONNECTOR")
    enable_webhook_connector: bool = Field(default=False, alias="ENABLE_WEBHOOK_CONNECTOR")

    n8n_webhook_url: str | None = Field(default=None, alias="N8N_WEBHOOK_URL")
    custom_webhook_url: str | None = Field(default=None, alias="CUSTOM_WEBHOOK_URL")
    slack_webhook_url: str | None = Field(default=None, alias="SLACK_WEBHOOK_URL")
    github_api_url: str | None = Field(default=None, alias="GITHUB_API_URL")
    github_token: str | None = Field(default=None, alias="GITHUB_TOKEN")
    github_repo: str | None = Field(default=None, alias="GITHUB_REPO")
    sheets_webhook_url: str | None = Field(default=None, alias="SHEETS_WEBHOOK_URL")

    openai_api_key: str | None = Field(default=None, alias="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4.1-mini", alias="OPENAI_MODEL")

    anthropic_api_key: str | None = Field(default=None, alias="ANTHROPIC_API_KEY")
    anthropic_model: str = Field(default="claude-3-5-haiku-latest", alias="ANTHROPIC_MODEL")

    gemini_api_key: str | None = Field(default=None, alias="GEMINI_API_KEY")
    gemini_model: str = Field(default="gemini-1.5-flash", alias="GEMINI_MODEL")

    @property
    def fallback_order(self) -> list[str]:
        return [item.strip() for item in self.provider_fallback_order.split(",") if item.strip()]

    @property
    def db_path(self) -> Path:
        path = Path(self.database_path)
        if not path.parent.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
        return path


@lru_cache
def get_settings() -> Settings:
    return Settings()
