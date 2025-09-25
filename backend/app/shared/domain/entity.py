import uuid
from pydantic import BaseModel, Field

class Entity(BaseModel):
    """
    The base class for entities in our pure domain model.
    Entities are defined by their unique identifier, not their attributes.
    """
    id: uuid.UUID = Field(default_factory=uuid.uuid4)

    # Pydantic v2 config to allow creating from ORM objects in the repository
    class Config:
        from_attributes = True

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
