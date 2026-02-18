from datetime import datetime, timezone, timedelta
from uuid import UUID
import psycopg

def day_bucket(ts: datetime) -> datetime:
    ts = ts.astimezone(timezone.utc)
    return ts.replace(hour=0, minute=0, second=0, microsecond=0)

def recompute_daily_bucket(conn: psycopg.Connection, user_id: UUID, day: datetime, typ: str):
    day_start = day_bucket(day)
    day_end = day_start + timedelta(days=1)

    with conn.cursor() as cur:
        # recompute from source of truth
        cur.execute(
            """
            SELECT
              COUNT(*) AS event_count,
              COALESCE(SUM(duration_seconds), 0) AS duration_seconds
            FROM activity_events
            WHERE user_id = %s
              AND type = %s
              AND started_at >= %s
              AND started_at < %s
            """,
            (str(user_id), typ, day_start, day_end),
        )
        row = cur.fetchone()
        event_count = int(row["event_count"])
        duration_seconds = int(row["duration_seconds"])

        # set exact values (idempotent)
        cur.execute(
            """
            INSERT INTO daily_aggregates (user_id, day, type, event_count, duration_seconds, updated_at)
            VALUES (%s, %s, %s, %s, %s, NOW())
            ON CONFLICT (user_id, day, type)
            DO UPDATE SET
              event_count = EXCLUDED.event_count,
              duration_seconds = EXCLUDED.duration_seconds,
              updated_at = NOW()
            """,
            (str(user_id), day_start, typ, event_count, duration_seconds),
        )
