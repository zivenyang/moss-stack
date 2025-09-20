import uuid
from pydantic import BaseModel
from sqlmodel.ext.asyncio.session import AsyncSession
from ..domain.item import ItemCreate, ItemPublic
from ..infra.item_repository import ItemRepository

class CreateItemCommand(BaseModel):
    item_in: ItemCreate
    owner_id: uuid.UUID

class CreateItemHandler:
    def __init__(self, session: AsyncSession):
        self.repo = ItemRepository(session)

    async def handle(self, command: CreateItemCommand) -> ItemPublic:
        new_item = await self.repo.create(item_in=command.item_in, owner_id=command.owner_id)
        return ItemPublic.model_validate(new_item)