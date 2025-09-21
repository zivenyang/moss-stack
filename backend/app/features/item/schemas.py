import uuid
from typing import Optional
from pydantic import BaseModel
from sqlmodel import SQLModel

# Base DTO with common fields
class ItemBase(SQLModel):
    name: str
    description: Optional[str] = None

# DTO for creating an item
class ItemCreate(ItemBase):
    pass

# DTO for updating an item (user context)
class ItemUpdate(BaseModel): # Using BaseModel as all fields are optional
    name: Optional[str] = None
    description: Optional[str] = None

# DTO for exposing an item to the public/users
class ItemPublic(ItemBase):
    id: uuid.UUID
    owner_id: uuid.UUID

# DTO for an admin updating an item
class ItemUpdateAdmin(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    owner_id: Optional[uuid.UUID] = None # Admin might be able to reassign an item