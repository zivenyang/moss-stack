import uuid
from pydantic import BaseModel
from app.shared.infrastructure.uow import IUnitOfWork
from app.shared.application.exceptions import ResourceNotFoundError
from app.features.item.schemas import ItemPublic
from app.features.item.infra.item_repository import ItemRepository

class GetItemByIdAdminQuery(BaseModel):
    item_id: uuid.UUID

class GetItemByIdAdminHandler:
    def __init__(self, uow: IUnitOfWork):
        self.uow = uow

    async def handle(self, query: GetItemByIdAdminQuery) -> ItemPublic:
        async with self.uow:
            repo = self.uow.get_repository(ItemRepository)
            
            # Use the admin-specific repository method
            db_item = await repo.get_by_id_admin(item_id=query.item_id)
            
            if not db_item:
                raise ResourceNotFoundError("Item not found.")
                
            return ItemPublic.model_validate(db_item)