import uuid
from pydantic import BaseModel
from app.shared.infrastructure.uow import IUnitOfWork
from app.shared.application.interfaces import ICommandHandler
from app.shared.application.exceptions import ResourceNotFoundError
from app.features.item.schemas import ItemUpdate, ItemPublic
from app.features.item.infra.item_repository import ItemRepository
from app.shared.infrastructure.logging.config import get_logger

logger = get_logger(__name__)


class UpdateItemCommand(BaseModel):
    item_id: uuid.UUID
    item_in: ItemUpdate
    owner_id: uuid.UUID


class UpdateItemHandler(ICommandHandler[UpdateItemCommand, ItemPublic]):
    def __init__(self, uow: IUnitOfWork):
        self.uow = uow

    async def handle(self, command: UpdateItemCommand) -> ItemPublic:
        logger.info("--> Entering UpdateItemHandler", item_id=str(command.item_id))
        async with self.uow:
            repo = self.uow.get_repository(ItemRepository)

            item = await repo.get(command.item_id, command.owner_id)
            logger.debug("Loaded item from repository", item_found=(item is not None))
            if not item or item.is_deleted:
                logger.warning(
                    "Item not found or deleted", item_id=str(command.item_id)
                )
                raise ResourceNotFoundError("Item not found.")

            self.uow.track(item)

            if command.item_in.name is not None:
                logger.debug("Updating item name", new_name=command.item_in.name)
                item.update_name(command.item_in.name)
            if command.item_in.description is not None:
                logger.debug(
                    "Updating item description", new_desc=command.item_in.description
                )
                item.update_description(command.item_in.description)

            logger.info("Calling repo.save() for item", item_id=str(item.id))
            await repo.save(item)

        logger.info("<-- Exiting UpdateItemHandler successfully", item_id=str(item.id))
        return ItemPublic.model_validate(item)
