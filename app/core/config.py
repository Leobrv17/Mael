from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class SecurityHeaders(BaseModel):
    enable_hsts: bool = Field(default=True)
    enable_frameguard: bool = Field(default=True)
    enable_content_type: bool = Field(default=True)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=False)

    app_name: str = "SaaS Backend"
    database_url: str = Field(default="sqlite+aiosqlite:///:memory:", alias="DATABASE_URL")
    firebase_project_id: str = Field(default="local-test-project", alias="FIREBASE_PROJECT_ID")
    firebase_credentials_path: str | None = Field(default=None, alias="FIREBASE_CREDENTIALS_PATH")
    app_base_url: str = Field(default="http://localhost:8000", alias="APP_BASE_URL")
    cors_origins: str = Field(default="*", alias="CORS_ORIGINS")
    smtp_host: str | None = Field(default=None, alias="SMTP_HOST")
    smtp_port: int | None = Field(default=None, alias="SMTP_PORT")
    smtp_user: str | None = Field(default=None, alias="SMTP_USER")
    smtp_password: str | None = Field(default=None, alias="SMTP_PASSWORD")
    security_headers: SecurityHeaders = SecurityHeaders()


settings = Settings()
