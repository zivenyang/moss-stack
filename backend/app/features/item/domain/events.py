import uuid
from typing import Optional
from app.shared.domain.event import DomainEvent

# Base event for Item aggregate for easy identification
class ItemEvent(DomainEvent):
    item_id: uuid.UUID

# Specific events capturing every state change
class ItemCreated(ItemEvent):
    owner_id: uuid.UUID
    name: str
    description: Optional[str]

class ItemNameUpdated(ItemEvent):
    new_name: str

class ItemDescriptionUpdated(ItemEvent):
    new_description: Optional[str]

class ItemDeleted(ItemEvent):
    pass