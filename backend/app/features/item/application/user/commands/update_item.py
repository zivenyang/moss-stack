import uuid
from pydantic import BaseModel
from sqlmodel.ext.asyncio.session import AsyncSession
from app.shared.application.result import Result
from app.shared.application.exceptions import ResourceNotFoundError
from app.features.item.domain.item import ItemUpdate, ItemPublic
from app.features.item.infra.item_repository import ItemRepository

class UpdateItemCommand(BaseModel):
    item_id: uuid.UUID
    item_in: ItemUpdate
    owner_id: uuid.UUID

class UpdateItemHandler:
    def __init__(self, session: AsyncSession):
        self.repo = ItemRepository(session)

    async def handle(self, command: UpdateItemCommand) -> Result[ItemPublic, ResourceNotFoundError]:
        """
        Handles the update of an existing item.
        """
        # 1. First, retrieve the item from the database
        db_item = await self.repo.get(item_id=command.item_id, owner_id=command.owner_id)

        # 2. Check if the item exists and belongs to the user
        if not db_item:
            return Result.failure(
                ResourceNotFoundError(f"Item with id {command.item_id} not found or you don't have permission.")
            )

        # 3. If it exists, update it with the new data
        updated_item = await self.repo.update(db_item=db_item, item_in=command.item_in)
        
        # 4. Return the updated item as a public DTO
        return Result.success(ItemPublic.model_validate(updated_item))