from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import Optional


class Settings(BaseSettings):
    # AWS/SQS
    aws_region: str = Field(default="us-east-1", validation_alias="AWS_REGION")

    # Prefer URL when available (AWS best practice)
    sqs_queue_url: Optional[str] = Field(default=None, validation_alias="SQS_QUEUE_URL")

    # Name-based resolution (LocalStack or AWS fallback)
    sqs_queue_name: str = Field(default="prodsight-events-queue", validation_alias="SQS_QUEUE_NAME")

    # Endpoint override ONLY for LocalStack; in AWS leave unset
    sqs_endpoint_url: Optional[str] = Field(default=None, validation_alias="SQS_ENDPOINT_URL")

    # Database
    db_dsn: str = Field(
        default="postgresql://postgres:mysecretpassword@localhost:5432/prodsight",
        validation_alias="DATABASE_URL",
    )

    # Worker tuning
    poll_wait_seconds: int = Field(default=10, validation_alias="POLL_WAIT_SECONDS")
    max_messages: int = Field(default=5, validation_alias="MAX_MESSAGES")

    model_config = SettingsConfigDict(
        env_prefix="",          # read exact env var names
        env_file=".env",
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()
