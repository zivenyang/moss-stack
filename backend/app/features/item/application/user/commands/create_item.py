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

            # 1. Execute domain logic to get the new aggregate and events
            new_item, events = Item.create(
                item_id=uuid.uuid4(),
                owner_id=command.owner_id,
                name=command.item_in.name,
                description=command.item_in.description,
            )

            # 2. Persist the events and the projection
            await repo.save_events(
                events=events, item_id=new_item.id, initial_version=0
            )
            await repo.save_projection(new_item)

            # 3. Add events to UoW for publishing to Kafka
            self.uow.add_events(events)

        return ItemPublic.model_validate(new_item)
