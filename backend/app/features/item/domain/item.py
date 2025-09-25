import uuid
from typing import Optional, List
from app.shared.domain.aggregate_root import AggregateRoot
from app.shared.domain.exceptions import BusinessRuleViolationError
from .events import (
    DomainEvent,
    ItemCreated,
    ItemNameUpdated,
    ItemDescriptionUpdated,
    ItemDeleted,
)


class Item(AggregateRoot):
    name: str
    description: Optional[str] = None
    owner_id: uuid.UUID
    is_deleted: bool = False
    version: int = 0

    @staticmethod
    def create(
        item_id: uuid.UUID, owner_id: uuid.UUID, name: str, description: Optional[str]
    ) -> "Item":
        item = Item(
            id=item_id, owner_id=owner_id, name=name, description=description, version=0
        )
        events = item.apply(
            ItemCreated(
                item_id=item.id,
                owner_id=item.owner_id,
                name=item.name,
                description=item.description,
            )
        )
        return item, events

    def update_name(self, new_name: str) -> List[DomainEvent]:
        if self.is_deleted:
            raise BusinessRuleViolationError("Cannot update a deleted item.")
        if new_name == self.name:
            return []
        self.name = new_name
        return self.apply(ItemNameUpdated(item_id=self.id, new_name=new_name))

    def update_description(self, new_description: Optional[str]) -> List[DomainEvent]:
        if self.is_deleted:
            raise BusinessRuleViolationError("Cannot update a deleted item.")
        if new_description == self.description:
            return []
        self.description = new_description
        return self.apply(
            ItemDescriptionUpdated(item_id=self.id, new_description=new_description)
        )

    def delete(self) -> List[DomainEvent]:
        if self.is_deleted:
            raise BusinessRuleViolationError("Item is already deleted.")
        self.is_deleted = True
        return self.apply(ItemDeleted(item_id=self.id))

    def apply(self, event: DomainEvent) -> List[DomainEvent]:
        """Applies an event, increments version, adds it to the event list, and returns it."""
        self.version += 1
        self._add_domain_event(event)
        return [event]
