# backend/app/shared/domain/entity.py

import uuid
from sqlmodel import SQLModel, Field

class Entity(SQLModel):
    """
    Base class for entities in the domain layer, built upon SQLModel.
    
    Entities have a unique identifier and a lifecycle. Their identity is defined by their ID,
    not their attributes. This base class provides a default UUID identifier.
    
    It also implements equality comparison based on the entity's ID, which is a
    fundamental concept in Domain-Driven Design.
    """
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    def __eq__(self, other: object) -> bool:
        """
        Entities are equal if they are of the same type and have the same ID.
        """
        if not isinstance(other, self.__class__):
            return NotImplemented
        return self.id == other.id

    def __hash__(self) -> int:
        """
        The hash of an entity is based on its unique identifier.
        """
        return hash(self.id)