import uuid
from typing import List, Optional, Tuple
from sqlmodel import select, func
from sqlmodel.ext.asyncio.session import AsyncSession

from ..domain.item import Item
from ..domain.events import DomainEvent
from ..domain.item_event_store import ItemEventStore
from .item_orm import ItemORM


class ItemRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    # --- Mapping Layer ---
    def _map_orm_to_domain(self, orm_item: ItemORM) -> Item:
        return Item.model_validate(orm_item)

    # --- Read Methods (Querying the Projection) ---
    async def get(self, item_id: uuid.UUID, owner_id: uuid.UUID) -> Optional[Item]:
        orm_item = (
            await self.session.exec(
                select(ItemORM).where(
                    ItemORM.id == item_id, ItemORM.owner_id == owner_id
                )
            )
        ).first()
        return self._map_orm_to_domain(orm_item) if orm_item else None

    async def get_by_id_admin(self, item_id: uuid.UUID) -> Optional[Item]:
        orm_item = await self.session.get(ItemORM, item_id)
        return self._map_orm_to_domain(orm_item) if orm_item else None

    async def get_multi_by_owner_paginated(
        self, owner_id: uuid.UUID, offset: int, limit: int
    ) -> Tuple[List[Item], int]:
        data_statement = (
            select(ItemORM)
            .where(ItemORM.owner_id == owner_id, ItemORM.is_deleted == False)
            .order_by(ItemORM.id.desc())
            .offset(offset)
            .limit(limit)
        )
        orm_items = (await self.session.exec(data_statement)).all()

        count_statement = (
            select(func.count())
            .select_from(ItemORM)
            .where(ItemORM.owner_id == owner_id, ItemORM.is_deleted == False)
        )
        total = (await self.session.exec(count_statement)).one()

        domain_items = [self._map_orm_to_domain(orm_item) for orm_item in orm_items]
        return domain_items, total

    async def get_multi_admin_paginated(
        self, offset: int, limit: int
    ) -> Tuple[List[Item], int]:
        data_statement = (
            select(ItemORM)
            .where(ItemORM.is_deleted == False)
            .order_by(ItemORM.id.desc())
            .offset(offset)
            .limit(limit)
        )
        orm_items = (await self.session.exec(data_statement)).all()

        count_statement = (
            select(func.count()).select_from(ItemORM).where(ItemORM.is_deleted == False)
        )
        total = (await self.session.exec(count_statement)).one()

        domain_items = [self._map_orm_to_domain(orm_item) for orm_item in orm_items]
        return domain_items, total

    # --- Write Methods (Saving Events and Projection) ---
    async def save_events(
        self, events: List[DomainEvent], item_id: uuid.UUID, initial_version: int
    ):
        current_version = initial_version
        for event in events:
            current_version += 1
            event_store_record = ItemEventStore(
                item_id=item_id,
                version=current_version,
                event_type=event.__class__.__name__,
                event_data=event.model_dump(mode="json"),
                occurred_on=event.occurred_on,
            )
            self.session.add(event_store_record)

    async def save_projection(self, item: Item):
        orm_item = await self.session.get(ItemORM, item.id)
        if orm_item:
            # Update existing ORM object
            update_data = item.model_dump()
            for key, value in update_data.items():
                setattr(orm_item, key, value)
        else:
            # Create new ORM object if it doesn't exist
            orm_item = ItemORM.model_validate(item)
            self.session.add(orm_item)
