import uuid
from pydantic import BaseModel
from app.shared.infrastructure.uow import IUnitOfWork
from app.shared.application.exceptions import ResourceNotFoundError
from app.features.item.schemas import ItemUpdateAdmin, ItemPublic
from app.features.item.infra.item_repository import ItemRepository

class UpdateItemAdminCommand(BaseModel):
    item_id: uuid.UUID
    item_in: ItemUpdateAdmin

class UpdateItemAdminHandler:
    def __init__(self, uow: IUnitOfWork):
        self.uow = uow

    async def handle(self, command: UpdateItemAdminCommand) -> ItemPublic:
        async with self.uow:
            repo = self.uow.get_repository(ItemRepository)
            
            db_item = await repo.get_by_id_admin(item_id=command.item_id)
            if not db_item:
                raise ResourceNotFoundError("Item not found.")
            
            updated_item = await repo.update(db_item=db_item, item_in=command.item_in)
            
        return ItemPublic.model_validate(updated_item)