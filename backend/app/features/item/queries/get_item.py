import uuid
from pydantic import BaseModel
from sqlmodel.ext.asyncio.session import AsyncSession
from ..domain.item import ItemPublic
from ..infra.item_repository import ItemRepository

class GetItemQuery(BaseModel):
    owner_id: uuid.UUID
    item_id: uuid.UUID

class GetItemHandler:
    def __init__(self, session: AsyncSession):
        self.repo = ItemRepository(session)

    async def handle(self, query: GetItemQuery) -> ItemPublic:
        item = await self.repo.get(
            owner_id=query.owner_id, item_id=query.item_id
        )
        return ItemPublic.model_validate(item)