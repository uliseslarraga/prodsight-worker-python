import logging
from uuid import UUID
from datetime import datetime

from .aggregates import day_bucket, recompute_daily_bucket

log = logging.getLogger("handler")


def fetch_event(conn, event_id: UUID, user_id: UUID):
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT id, user_id, type, started_at, ended_at, duration_seconds
            FROM activity_events
            WHERE id = %s AND user_id = %s
            """,
            (str(event_id), str(user_id)),
        )
        return cur.fetchone()


def handle_message(conn, msg):
    """
    msg is EventChangedMessage (pydantic model)
    """

    if msg.eventType == "EventCreated":
        ev = fetch_event(conn, msg.eventId, msg.userId)

        if not ev:
            log.warning(
                "event_not_found",
                extra={"eventId": str(msg.eventId), "userId": str(msg.userId)},
            )
            return  # <- SAFE: inside function

        day = day_bucket(ev["started_at"])

        recompute_daily_bucket(
            conn=conn,
            user_id=msg.userId,
            day=day,
            typ=ev["type"],
        )

        log.info(
            "aggregate_recomputed",
            extra={
                "userId": str(msg.userId),
                "day": day.isoformat(),
                "type": ev["type"],
            },
        )

    elif msg.eventType in ("EventUpdated", "EventDeleted"):
        log.info(
            "noop_event_type",
            extra={"eventType": msg.eventType, "eventId": str(msg.eventId)},
        )
