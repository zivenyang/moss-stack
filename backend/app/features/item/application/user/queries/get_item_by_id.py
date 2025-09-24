import uuid
from pydantic import BaseModel

from app.shared.infrastructure.uow import IUnitOfWork
from app.shared.application.interfaces import IQueryHandler
from app.shared.application.exceptions import ResourceNotFoundError
from app.features.item.schemas import ItemPublic
from app.features.item.infra.item_repository import ItemRepository

class GetItemByIdQuery(BaseModel):
    """Query to retrieve a single item by its ID, ensuring ownership."""
    item_id: uuid.UUID
    owner_id: uuid.UUID

class GetItemByIdHandler(IQueryHandler[GetItemByIdQuery, ItemPublic]):
    """

    Handler for the GetItemByIdQuery. It fetches a single item,
    verifying that it belongs to the specified owner.
    """
    def __init__(self, uow: IUnitOfWork):
        self.uow = uow

    async def handle(self, query: GetItemByIdQuery) -> ItemPublic:
        async with self.uow:
            repo = self.uow.get_repository(ItemRepository)
            
            # The repository's 'get' method correctly enforces ownership
            db_item = await repo.get(item_id=query.item_id, owner_id=query.owner_id)
            
            if not db_item or db_item.is_deleted:
                raise ResourceNotFoundError("Item not found or you don't have permission.")
        
        # Post-transaction processing
        return ItemPublic.model_validate(db_item)