# ProdSight Worker (Python)

Background worker service for the **ProdSight** system.

This service consumes messages from **SQS (LocalStack locally, AWS in
cloud)** and maintains precomputed aggregates in PostgreSQL.

------------------------------------------------------------------------

# Architecture Role

The worker is responsible for:

-   Polling SQS for domain events (e.g. `EventCreated`)
-   Fetching authoritative data from `activity_events`
-   Recomputing daily aggregates
-   Updating `daily_aggregates` table
-   Handling retries & idempotency

It does NOT: - Expose HTTP endpoints - Modify core event records -
Accept external traffic

------------------------------------------------------------------------

# Local Development Setup

## 1. Start Infrastructure

You need:

-   PostgreSQL
-   LocalStack (SQS)

Example using Docker:

``` bash
docker compose up -d postgres localstack
```

Verify LocalStack:

``` bash
curl http://localhost:4566/health
```

------------------------------------------------------------------------

## 2. Create Queue (LocalStack)

``` bash
aws --endpoint-url=http://localhost:4566 sqs create-queue   --queue-name prodsight-events-queue
```

------------------------------------------------------------------------

## 3. Environment Variables

Export these before running the worker locally:

``` bash
export AWS_REGION=us-east-1
export AWS_ACCESS_KEY_ID=test
export AWS_SECRET_ACCESS_KEY=test
export SQS_ENDPOINT_URL=http://localhost:4566
export SQS_QUEUE_NAME=prodsight-events-queue
export DATABASE_URL=postgresql://prodsight:prodsight@localhost:5432/prodsight
```

------------------------------------------------------------------------

## 4. Run Worker

Using virtualenv:

``` bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

python -m app.main
```

You should see:

``` json
{
  "message": "worker_started",
  "queue_url": "...",
  "sqs_endpoint": "..."
}
```

------------------------------------------------------------------------

# Database Requirements

The worker expects:

## activity_events

Source-of-truth table created by API.

## daily_aggregates

``` sql
CREATE TABLE IF NOT EXISTS daily_aggregates (
  user_id UUID NOT NULL,
  day TIMESTAMPTZ NOT NULL,
  type TEXT NOT NULL,
  event_count BIGINT NOT NULL DEFAULT 0,
  duration_seconds BIGINT NOT NULL DEFAULT 0,
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  PRIMARY KEY (user_id, day, type)
);
```

------------------------------------------------------------------------

# Idempotency Strategy

The worker is designed to be safe under:

-   At-least-once delivery
-   Message retries
-   Duplicate deliveries

Instead of incrementing blindly, it **recomputes aggregates from the
source table** on each message.

This guarantees correct results even if the same message is processed
multiple times.

------------------------------------------------------------------------

# CI Pipeline

CI performs:

-   Python dependency installation
-   Linting (ruff)
-   Tests (pytest)
-   Docker image build
-   Push to GHCR

Image naming:

    ghcr.io/<owner>/<repo>:main
    ghcr.io/<owner>/<repo>:sha-<commit>

------------------------------------------------------------------------

# Docker Usage

Build locally:

``` bash
docker build -t prodsight-worker .
```

Run:

``` bash
docker run --rm   -e AWS_REGION=us-east-1   -e AWS_ACCESS_KEY_ID=test   -e AWS_SECRET_ACCESS_KEY=test   -e SQS_ENDPOINT_URL=http://host.docker.internal:4566   -e SQS_QUEUE_NAME=prodsight-events-queue   -e DATABASE_URL=postgresql://prodsight:prodsight@host.docker.internal:5432/prodsight   prodsight-worker
```

------------------------------------------------------------------------

# Troubleshooting

### Worker logs too many messages

-   Check SQS queue backlog
-   Purge queue in LocalStack if needed:

``` bash
aws --endpoint-url=http://localhost:4566 sqs purge-queue   --queue-url <queue-url>
```

------------------------------------------------------------------------

### Outbox row stuck in PENDING

-   Verify API scheduler is running
-   Verify SQS endpoint config
-   Check `last_error` column in `outbox_events`

------------------------------------------------------------------------

# Cloud Migration Notes

When moving to AWS:

-   Remove `SQS_ENDPOINT_URL`
-   Use IAM role instead of static credentials
-   Replace LocalStack queue URL with real AWS SQS URL

------------------------------------------------------------------------

# License

Personal DevOps / SRE practice project.
