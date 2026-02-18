from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    aws_region: str = "us-east-1"
    sqs_queue_name: str = "prodsight-events-queue"
    sqs_endpoint_url: str | None = "http://localhost:4566"  # e.g. http://localstack:4566
    db_dsn: str = "postgresql://postgres:mysecretpassword@localhost:5432/prodsight"
    poll_wait_seconds: int = 10
    max_messages: int = 5

    class Config:
        env_prefix = ""
        env_file = ".env"
        case_sensitive = False

settings = Settings()
