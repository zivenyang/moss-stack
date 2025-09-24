import uuid
from typing import Optional
from sqlmodel import Field
from app.shared.domain.aggregate_root import AggregateRoot
from app.shared.domain.exceptions import BusinessRuleViolationError
from .events import ItemCreated, ItemNameUpdated, ItemDescriptionUpdated, ItemDeleted

class Item(AggregateRoot, table=True):
    """
    The Item aggregate root.
    This table acts as a "Projection" or "Materialized View" for fast queries.
    Its state is derived from the event stream.
    """
    # Projection fields
    id: uuid.UUID = Field(primary_key=True, nullable=False)
    name: str = Field(index=True)
    description: Optional[str] = None
    owner_id: uuid.UUID = Field(foreign_key="user.id", nullable=False)
    is_deleted: bool = Field(default=False, index=True)
    version: int = Field(default=0) # For optimistic concurrency

    # --- Factory and Business Methods ---
    @staticmethod
    def create(item_id: uuid.UUID, owner_id: uuid.UUID, name: str, description: Optional[str]) -> "Item":
        item = Item(id=item_id, owner_id=owner_id, name=name, description=description, version=1)
        item._add_domain_event(
            ItemCreated(item_id=item.id, owner_id=item.owner_id, name=item.name, description=item.description)
        )
        return item

    def update_name(self, new_name: str):
        if self.is_deleted:
            raise BusinessRuleViolationError("Cannot update a deleted item.")
        if new_name == self.name: 
            return
        
        self.name = new_name
        self._add_domain_event(ItemNameUpdated(item_id=self.id, new_name=new_name))

    def update_description(self, new_description: Optional[str]):
        if self.is_deleted:
            raise BusinessRuleViolationError("Cannot update a deleted item.")
        if new_description == self.description: 
            return

        self.description = new_description
        self._add_domain_event(ItemDescriptionUpdated(item_id=self.id, new_description=new_description))

    def delete(self):
        if self.is_deleted:
            raise BusinessRuleViolationError("Item is already deleted.")
        self.is_deleted = True
        self._add_domain_event(ItemDeleted(item_id=self.id))