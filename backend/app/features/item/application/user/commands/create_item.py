import uuid
from pydantic import BaseModel
from app.shared.infrastructure.uow import IUnitOfWork
from app.shared.application.interfaces import ICommandHandler
from app.features.item.infra.item_repository import ItemRepository
from app.features.item.domain.item import Item
from app.features.item.schemas import ItemCreate, ItemPublic


class CreateItemCommand(BaseModel):
    item_in: ItemCreate
    owner_id: uuid.UUID


class CreateItemHandler(ICommandHandler[CreateItemCommand, ItemPublic]):
    def __init__(self, uow: IUnitOfWork):
        self.uow = uow

    async def handle(self, command: CreateItemCommand) -> ItemPublic:
        async with self.uow:
            repo = self.uow.get_repository(ItemRepository)

            new_item = Item.create(
                item_id=uuid.uuid4(),
                owner_id=command.owner_id,
                name=command.item_in.name,
                description=command.item_in.description,
            )

            # Explicitly track the new aggregate for event publishing
            self.uow.track(new_item)

            await repo.save(new_item)
            # UoW will commit and publish events upon exiting the 'with' block

        return ItemPublic.model_validate(new_item)
