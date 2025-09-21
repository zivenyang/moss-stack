import uuid
from typing import List
from pydantic import BaseModel, Field
from app.shared.infrastructure.uow import IUnitOfWork
from app.features.item.schemas import ItemPublic
from app.features.item.infra.item_repository import ItemRepository

class GetItemListQuery(BaseModel):
    """
    Query to retrieve a list of items belonging to a specific owner, with pagination.
    """
    owner_id: uuid.UUID
    skip: int = Field(0, ge=0, description="Number of items to skip")
    limit: int = Field(100, gt=0, le=100, description="Number of items to return")

class GetItemListHandler:
    """
    Handler for the GetItemListQuery. It fetches a paginated list of items
    for a specific user from the repository.
    """
    def __init__(self, uow: IUnitOfWork):
        self.uow = uow

    async def handle(self, query: GetItemListQuery) -> List[ItemPublic]:
        async with self.uow:
            # Get the repository instance from the Unit of Work
            repo = self.uow.get_repository(ItemRepository)
            
            # Call the repository method that enforces ownership and pagination
            items = await repo.get_multi_by_owner(
                owner_id=query.owner_id, skip=query.skip, limit=query.limit
            )
            
            # Convert domain models to public DTOs
            return [ItemPublic.model_validate(item) for item in items]