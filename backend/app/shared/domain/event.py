import uuid
from datetime import datetime, timezone
from pydantic import BaseModel, Field


class DomainEvent(BaseModel):
    """

    Base class for domain events.
    A domain event is something that happened in the past that is of interest
    to business experts.
    """

    event_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    occurred_on: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
