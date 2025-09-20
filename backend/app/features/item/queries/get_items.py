import uuid
from typing import List
from pydantic import BaseModel
from sqlmodel.ext.asyncio.session import AsyncSession
from ..domain.item import ItemPublic
from ..infra.item_repository import ItemRepository

class GetItemsQuery(BaseModel):
    owner_id: uuid.UUID
    skip: int = 0
    limit: int = 100

class GetItemsHandler:
    def __init__(self, session: AsyncSession):
        self.repo = ItemRepository(session)

    async def handle(self, query: GetItemsQuery) -> List[ItemPublic]:
        items = await self.repo.get_multi_by_owner(
            owner_id=query.owner_id, skip=query.skip, limit=query.limit
        )
        return [ItemPublic.model_validate(item) for item in items]