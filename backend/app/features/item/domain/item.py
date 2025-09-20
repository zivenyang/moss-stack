import uuid
from typing import Optional
from sqlmodel import Field
from app.shared.domain.aggregate_root import AggregateRoot

# Pydantic-only models for API (DTOs)
# ------------------------------------
class ItemBase(AggregateRoot): # 继承AggregateRoot以获得id
    name: str = Field(index=True)
    description: Optional[str] = None

class ItemCreate(ItemBase):
    pass

class ItemUpdate(ItemBase):
    name: Optional[str] = None # 在更新时，字段可以是可选的
    description: Optional[str] = None

class ItemPublic(ItemBase):
    owner_id: uuid.UUID


# Database table model
# --------------------
class Item(ItemBase, table=True):
    # 'id' 字段继承自 AggregateRoot -> Entity
    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        nullable=False,
    )
    owner_id: uuid.UUID = Field(foreign_key="user.id", nullable=False)