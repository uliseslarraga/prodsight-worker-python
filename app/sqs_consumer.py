import json
import logging
import boto3
from botocore.config import Config
from .config import settings

log = logging.getLogger("sqs_consumer")

def make_sqs_client():
    # If endpoint_url is provided, boto3 will use it (LocalStack).
    cfg = Config(region_name=settings.aws_region)
    return boto3.client("sqs", region_name=settings.aws_region, endpoint_url=settings.sqs_endpoint_url, config=cfg)

def ensure_queue(settings) -> str:
    if settings.sqs_queue_url:
        return settings.sqs_queue_url

    # Fallback: resolve from name (LocalStack or AWS)
    sqs = boto3.client(
        "sqs",
        region_name=settings.aws_region,
        endpoint_url=settings.sqs_endpoint_url,
    )
    return sqs.get_queue_url(QueueName=settings.sqs_queue_name)["QueueUrl"]

def receive_messages(sqs, queue_url: str, max_messages: int, wait_seconds: int):
    return sqs.receive_message(
        QueueUrl=queue_url,
        MaxNumberOfMessages=max_messages,
        WaitTimeSeconds=wait_seconds,
        MessageAttributeNames=["All"],
    )

def delete_message(sqs, queue_url: str, receipt_handle: str):
    sqs.delete_message(QueueUrl=queue_url, ReceiptHandle=receipt_handle)

def poll_loop(queue_url: str, handler_fn):
    sqs = make_sqs_client()
    log.info("poll_loop_start", extra={"queue_url": queue_url, "endpoint": settings.sqs_endpoint_url})
    while True:
        resp = receive_messages(sqs, queue_url, settings.max_messages, settings.poll_wait_seconds)
        messages = resp.get("Messages", [])
        if not messages:
            continue

        for m in messages:
            msg_id = m.get("MessageId")
            log.info("processing_message", extra={"messageId": msg_id})
            receipt = m["ReceiptHandle"]
            body = m.get("Body", "")
            try:
                payload = json.loads(body)
                # Validate shape with pydantic
                from .models import EventChangedMessage
                msg = EventChangedMessage.model_validate(payload)
                handler_fn(msg)
                delete_message(sqs, queue_url, receipt)
                log.info("message_deleted", extra={"messageId": msg_id})
            except Exception as e:
                log.exception("message_processing_failed", extra={"error": str(e), "body": body})
                # Don't delete: rely on SQS redrive policy / DLQ (LocalStack supports redrive if configured)
