import logging
from .logging import setup_logging
from .config import settings
from .db import get_conn
from .sqs_consumer import ensure_queue, poll_loop, make_sqs_client
from .handler import handle_message

def main():
    setup_logging()
    logger = logging.getLogger("main")

    # DB conn
    conn = get_conn()

    sqs = make_sqs_client()
    queue_url = ensure_queue(settings)

    logger.info(
        "worker_started",
        extra={
            "queue_url": queue_url,
            "sqs_endpoint": settings.sqs_endpoint_url,
            "region": settings.aws_region,
        },
    )

    def handler(msg):
        with conn.transaction():
            handle_message(conn, msg)


    poll_loop(queue_url, handler)

if __name__ == "__main__":
    main()
