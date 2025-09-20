import uuid
from pydantic import BaseModel, Field

class Entity(BaseModel):
    """
    Base class for entities in the domain layer.
    Entities have a unique identifier and a lifecycle.
    Their identity is defined by their ID, not their attributes.
    """
    id: uuid.UUID = Field(default_factory=uuid.uuid4)

    # Pydantic configuration to allow ORM mode
    class Config:
        orm_mode = True # Deprecated, use from_attributes=True in Pydantic V2
        from_attributes = True

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Entity):
            return NotImplemented
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)