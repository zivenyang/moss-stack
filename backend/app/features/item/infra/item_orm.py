import uuid
from typing import Optional
from sqlmodel import Field, SQLModel

class ItemORM(SQLModel, table=True):
    """
    The ORM model for the 'item' table. Its only responsibility is to map
    the database table structure.
    """
    __tablename__ = "item" # Explicitly define table name

    id: uuid.UUID = Field(primary_key=True)
    name: str = Field(index=True)
    description: Optional[str] = None
    owner_id: uuid.UUID = Field(foreign_key="user.id")
    is_deleted: bool = Field(default=False, index=True)
    version: int = Field(default=0)