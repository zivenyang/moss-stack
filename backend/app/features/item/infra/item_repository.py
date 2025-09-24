import uuid
from typing import List, Optional, Tuple
from sqlmodel import select, func
from sqlmodel.ext.asyncio.session import AsyncSession

from app.shared.infrastructure.logging.config import get_logger
from ..domain.item import Item
from ..domain.item_event_store import ItemEventStore

logger = get_logger(__name__)


class ItemRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, item_id: uuid.UUID, owner_id: uuid.UUID) -> Optional[Item]:
        """
        Gets a single item by its ID, ensuring it belongs to the specified owner.
        """
        # 我们不再使用 session.get，因为它只能按主键查询
        # 我们需要一个带有 WHERE 子句的 select 语句
        statement = select(Item).where(Item.id == item_id, Item.owner_id == owner_id)
        result = await self.session.exec(statement)
        return result.first()

    async def save(self, item: Item) -> None:
        """
        Persists the aggregate's state changes.
        This includes storing new domain events and updating the read projection.
        """
        # 1. Store the new domain events
        current_version = item.version
        for event in item.domain_events:
            event_store_record = ItemEventStore(
                item_id=item.id,
                version=current_version + 1,
                event_type=event.__class__.__name__,
                event_data=event.model_dump(mode="json", exclude={"item_id"}),
                occurred_on=event.occurred_on,
            )
            self.session.add(event_store_record)
            current_version += 1

        # 2. Update the version on the projection model
        item.version = current_version

        # 3. Add (for new) or merge (for existing) the projection state
        self.session.add(item)

    # --- Query methods still read from the fast projection table ---
    async def get_multi_by_owner_paginated(
        self, owner_id: uuid.UUID, offset: int, limit: int
    ) -> Tuple[List[Item], int]:
        data_statement = (
            select(Item)
            .where(Item.owner_id == owner_id, Item.is_deleted.is_(False))
            .order_by(Item.id.desc())
            .offset(offset)
            .limit(limit)
        )
        items = (await self.session.exec(data_statement)).all()

        count_statement = (
            select(func.count())
            .select_from(Item)
            .where(Item.owner_id == owner_id, Item.is_deleted.is_(False))
        )
        total = (await self.session.exec(count_statement)).one()

        return items, total

    async def get_multi_admin_paginated(
        self, offset: int, limit: int
    ) -> Tuple[List[Item], int]:
        # Similar logic, just without the owner_id filter
        data_statement = (
            select(Item)
            .where(Item.is_deleted.is_(False))
            .order_by(Item.id.desc())
            .offset(offset)
            .limit(limit)
        )
        items = (await self.session.exec(data_statement)).all()

        count_statement = (
            select(func.count()).select_from(Item).where(Item.is_deleted.is_(False))
        )
        total = (await self.session.exec(count_statement)).one()

        return items, total
