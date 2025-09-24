import uuid
from pydantic import BaseModel
from app.shared.infrastructure.uow import IUnitOfWork
from app.shared.application.interfaces import ICommandHandler
from app.shared.application.exceptions import ResourceNotFoundError
from app.features.item.infra.item_repository import ItemRepository

class DeleteItemCommand(BaseModel):
    """Command to delete an item, ensuring ownership."""
    item_id: uuid.UUID
    owner_id: uuid.UUID

class DeleteItemHandler(ICommandHandler[DeleteItemCommand, None]):
    """
    Handler for the DeleteItemCommand. It marks an item as deleted
    by executing its domain method, which in turn creates a domain event.
    """
    def __init__(self, uow: IUnitOfWork):
        self.uow = uow

    async def handle(self, command: DeleteItemCommand) -> None:
        async with self.uow:
            repo = self.uow.get_repository(ItemRepository)
            
            # 1. Load the aggregate root, ensuring it belongs to the current user
            item = await repo.get(item_id=command.item_id, owner_id=command.owner_id)
            if not item:
                # We can choose to be idempotent: if it's already gone, that's a success.
                # However, for clearer feedback, we'll raise an error if not found.
                raise ResourceNotFoundError("Item not found.")
            
            # 2. Track the aggregate for event publishing
            self.uow.track(item)
            
            # 3. Execute the business method on the domain model
            # This will create the ItemDeleted event and set is_deleted = True
            item.delete()
            
            # 4. Persist the changes (new event and updated projection)
            await repo.save(item)
            
            # The UoW will commit the transaction and publish the ItemDeleted event
            # upon exiting the 'with' block.