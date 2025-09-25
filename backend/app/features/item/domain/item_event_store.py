import uuid
from datetime import datetime, timezone
from sqlalchemy.types import DateTime 
from typing import Dict, Any
from sqlmodel import Field, SQLModel, JSON, Column


class ItemEventStore(SQLModel, table=True):
    """
    ORM model for storing the immutable log of domain events for Items.
    This is the "Source of Truth" for the Item aggregate.
    """

    event_id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    item_id: uuid.UUID = Field(index=True)
    version: int  # This would be the next field to add for optimistic concurrency
    event_type: str
    event_data: Dict[str, Any] = Field(sa_column=Column(JSON))
    occurred_on: datetime = Field(
        sa_column=Column(DateTime(timezone=True), nullable=False)
    )
