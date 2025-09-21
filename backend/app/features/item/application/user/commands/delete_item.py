import uuid
from pydantic import BaseModel
from sqlmodel.ext.asyncio.session import AsyncSession
from app.shared.application.result import Result
from app.shared.application.exceptions import ResourceNotFoundError
from app.features.item.infra.item_repository import ItemRepository


class DeleteItemCommand(BaseModel):
    item_id: uuid.UUID
    owner_id: uuid.UUID


class DeleteItemHandler:
    def __init__(self, session: AsyncSession):
        self.repo = ItemRepository(session)

    async def handle(
        self, command: DeleteItemCommand
    ) -> Result[None, ResourceNotFoundError]:
        """
        Handles the deletion of an existing item.
        """
        # 1. Retrieve the item to ensure it exists and belongs to the user
        db_item = await self.repo.get(
            item_id=command.item_id, owner_id=command.owner_id
        )

        # 2. Check for existence and ownership
        if not db_item:
            return Result.failure(
                ResourceNotFoundError(
                    f"Item with id {command.item_id} not found or you don't have permission."
                )
            )

        # 3. If valid, proceed with deletion
        await self.repo.remove(db_item=db_item)

        # 4. On successful deletion, return a success result with no value
        return Result.success(None)
