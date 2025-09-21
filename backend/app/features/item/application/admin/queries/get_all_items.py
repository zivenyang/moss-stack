from typing import List
from pydantic import BaseModel, Field
from app.shared.infrastructure.uow import IUnitOfWork
from app.features.item.schemas import ItemPublic
from app.features.item.infra.item_repository import ItemRepository

class GetAllItemsAdminQuery(BaseModel):
    """
    Query for an admin to retrieve a list of all items in the system, with pagination.
    """
    skip: int = Field(0, ge=0, description="Number of items to skip")
    limit: int = Field(100, gt=0, le=100, description="Number of items to return")

class GetAllItemsAdminHandler:
    """
    Handler for the GetAllItemsAdminQuery. It fetches a paginated list of all items
    from the repository, without any ownership checks.
    """
    def __init__(self, uow: IUnitOfWork):
        self.uow = uow

    async def handle(self, query: GetAllItemsAdminQuery) -> List[ItemPublic]:
        async with self.uow:
            # Get the repository instance
            repo = self.uow.get_repository(ItemRepository)
            
            # Call the admin-specific repository method
            items = await repo.get_multi_admin(skip=query.skip, limit=query.limit)
            
            # Convert domain models to public DTOs
            return [ItemPublic.model_validate(item) for item in items]