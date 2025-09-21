import uuid
from pydantic import BaseModel
from app.shared.infrastructure.uow import IUnitOfWork
from app.features.item.infra.item_repository import ItemRepository
from app.features.item.domain.item import Item
from app.features.item.schemas import ItemCreate, ItemPublic

class CreateItemCommand(BaseModel):
    item_in: ItemCreate
    owner_id: uuid.UUID

class CreateItemHandler:
    def __init__(self, uow: IUnitOfWork):
        self.uow = uow

    async def handle(self, command: CreateItemCommand) -> ItemPublic:
        async with self.uow:
            repo = self.uow.get_repository(ItemRepository)
            
            # Here we create the domain model instance directly
            db_item = Item.model_validate(command.item_in, update={"owner_id": command.owner_id})
            
            self.uow.session.add(db_item)
            # UoW handles commit
            
        return ItemPublic.model_validate(db_item)