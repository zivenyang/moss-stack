import uuid
from typing import List, Optional
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from ..domain.item import Item, ItemCreate, ItemUpdate

class ItemRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, item_id: uuid.UUID, owner_id: uuid.UUID) -> Optional[Item]:
        statement = select(Item).where(Item.id == item_id, Item.owner_id == owner_id)
        result = await self.session.exec(statement)
        return result.first()

    async def get_multi_by_owner(self, owner_id: uuid.UUID, skip: int = 0, limit: int = 100) -> List[Item]:
        statement = select(Item).where(Item.owner_id == owner_id).offset(skip).limit(limit)
        result = await self.session.exec(statement)
        return result.all()

    async def create(self, item_in: ItemCreate, owner_id: uuid.UUID) -> Item:
        db_item = Item.model_validate(item_in, update={"owner_id": owner_id})
        self.session.add(db_item)
        await self.session.commit()
        await self.session.refresh(db_item)
        return db_item

    async def update(self, db_item: Item, item_in: ItemUpdate) -> Item:
        item_data = item_in.model_dump(exclude_unset=True)
        for key, value in item_data.items():
            setattr(db_item, key, value)
        self.session.add(db_item)
        await self.session.commit()
        await self.session.refresh(db_item)
        return db_item

    async def remove(self, db_item: Item) -> None:
        await self.session.delete(db_item)
        await self.session.commit()