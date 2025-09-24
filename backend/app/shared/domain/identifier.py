import uuid
from sqlmodel import SQLModel, Field
from .identifier import Identifier

class Entity(SQLModel):
    """Base class for entities. Uses a generic Identifier type."""
    id: Identifier = Field(default_factory=uuid.uuid4, primary_key=True)
    
    # ... (__eq__, __hash__ methods remain the same)