import uuid
from typing import List, Optional, Tuple
from sqlmodel import select, func
from sqlmodel.ext.asyncio.session import AsyncSession
from ..domain.item import Item
from ..schemas import ItemCreate, ItemUpdate


class ItemRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, item_id: uuid.UUID, owner_id: uuid.UUID) -> Optional[Item]:
        statement = select(Item).where(Item.id == item_id, Item.owner_id == owner_id)
        result = await self.session.exec(statement)
        return result.first()

    async def get_multi_by_owner_paginated(
        self, owner_id: uuid.UUID, offset: int = 0, limit: int = 100
    ) -> Tuple[List[Item], int]:
        """
        Gets a paginated list of items for an owner and the total count.
        """
        # --- Query for the data ---
        data_statement = (
            select(Item)
            .where(Item.owner_id == owner_id)
            .order_by(Item.id.desc())  # Or another consistent order
            .offset(offset)
            .limit(limit)
        )

        # --- Query for the total count ---
        # We build a separate query for the count for clarity and performance.
        count_statement = (
            select(func.count()).select_from(Item).where(Item.owner_id == owner_id)
        )

        # --- Execute both queries ---
        # In a real high-performance scenario, one might run these concurrently
        # with asyncio.gather, but for simplicity, sequential is fine.
        data_result = await self.session.exec(data_statement)
        items = data_result.all()

        count_result = await self.session.exec(count_statement)
        total = count_result.one()

        return items, total

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

    async def get_multi_admin_paginated(
        self, skip: int = 0, limit: int = 100
    ) -> Tuple[List[Item], int]:
        """
        Gets a paginated list of all items and the total count.
        """
        data_statement = select(Item).order_by(Item.id.desc()).offset(skip).limit(limit)
        items = (await self.session.exec(data_statement)).all()

        count_statement = select(func.count()).select_from(Item)
        total = (await self.session.exec(count_statement)).one()

        return items, total
