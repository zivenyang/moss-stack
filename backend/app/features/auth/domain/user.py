import uuid
from typing import Optional
from sqlmodel import Field, SQLModel

class UserBase(SQLModel):
    username: str = Field(index=True, unique=True, max_length=50)
    email: str = Field(unique=True, index=True, max_length=100)
    is_active: bool = Field(default=True)
    is_superuser: bool = Field(default=False)

class User(UserBase, table=True):
    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str = Field(nullable=False)

# Pydantic-only models for API operations
class UserCreate(UserBase):
    password: str = Field(min_length=8)

class UserPublic(UserBase):
    id: uuid.UUID