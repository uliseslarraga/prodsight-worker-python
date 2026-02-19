from __future__ import annotations

from typing import Optional
from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # AWS/SQS
    aws_region: str = Field(default="us-east-1", validation_alias="AWS_REGION")
    sqs_queue_url: Optional[str] = Field(default=None, validation_alias="SQS_QUEUE_URL")
    sqs_queue_name: str = Field(default="prodsight-events-queue", validation_alias="SQS_QUEUE_NAME")
    sqs_endpoint_url: Optional[str] = Field(default=None, validation_alias="SQS_ENDPOINT_URL")

    # Database: prefer DATABASE_URL, else build from DB_*
    database_url: Optional[str] = Field(default=None, validation_alias="DATABASE_URL")

    db_host: Optional[str] = Field(default=None, validation_alias="DB_HOST")
    db_port: int = Field(default=5432, validation_alias="DB_PORT")
    db_name: Optional[str] = Field(default=None, validation_alias="DB_NAME")
    db_user: Optional[str] = Field(default=None, validation_alias="DB_USER")
    db_password: Optional[str] = Field(default=None, validation_alias="DB_PASSWORD")

    # Worker tuning
    poll_wait_seconds: int = Field(default=10, validation_alias="POLL_WAIT_SECONDS")
    max_messages: int = Field(default=5, validation_alias="MAX_MESSAGES")

    model_config = SettingsConfigDict(
        env_prefix="",
        env_file=".env",
        case_sensitive=False,
        extra="ignore",
    )

    @model_validator(mode="after")
    def build_database_url(self):
        # 1) Local: if DATABASE_URL exists, use it
        if self.database_url and self.database_url.strip():
            return self

        # 2) AWS/ECS: build from DB_* parts
        missing = [k for k in ("db_host", "db_name", "db_user", "db_password") if not getattr(self, k)]
        if missing:
            raise ValueError(
                "Missing database configuration. "
                "Set DATABASE_URL (local) or DB_HOST/DB_NAME/DB_USER/DB_PASSWORD (ECS). "
                f"Missing: {missing}"
            )

        self.database_url = (
            f"postgresql://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )
        return self

    @property
    def db_dsn(self) -> str:
        # keep backward compatibility with your code
        return self.database_url  # type: ignore[return-value]


settings = Settings()