import uuid
from typing import Optional
from sqlmodel import Field
from app.shared.domain.aggregate_root import AggregateRoot

# The Item aggregate root and database table model.
class Item(AggregateRoot, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, nullable=False)
    name: str = Field(index=True)
    description: Optional[str] = None
    owner_id: uuid.UUID = Field(foreign_key="user.id", nullable=False)