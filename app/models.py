from pydantic import BaseModel, Field
from typing import Literal
from uuid import UUID
from datetime import datetime

EventType = Literal["EventCreated", "EventUpdated", "EventDeleted"]

class EventChangedMessage(BaseModel):
    eventType: EventType
    eventId: UUID
    userId: UUID
    occurredAt: datetime
    version: int = Field(default=1)
