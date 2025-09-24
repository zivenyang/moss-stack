import uuid
from pydantic import BaseModel

from app.shared.infrastructure.uow import IUnitOfWork
from app.shared.application.interfaces import IQueryHandler
from app.shared.schemas import Paginated, PageParams
from app.features.item.schemas import ItemPublic
from app.features.item.infra.item_repository import ItemRepository


class GetItemListQuery(BaseModel):
    """
    Query to retrieve a list of items belonging to a specific owner, with pagination.
    """

    owner_id: uuid.UUID
    page_params: PageParams


class GetItemListHandler(IQueryHandler[GetItemListQuery, Paginated[ItemPublic]]):
    """
    Handler for the GetItemListQuery. It fetches a paginated list of items
    for a specific user from the repository.
    """

    def __init__(self, uow: IUnitOfWork):
        self.uow = uow

    async def handle(self, query: GetItemListQuery) -> Paginated[ItemPublic]:
        items_from_db = []
        total_count = 0

        # For read-only operations, the UoW primarily serves to provide a session
        # and a consistent way to access repositories.
        async with self.uow:
            repo = self.uow.get_repository(ItemRepository)
            items_from_db, total_count = await repo.get_multi_by_owner_paginated(
                owner_id=query.owner_id,
                offset=query.page_params.offset,
                limit=query.page_params.size,
            )

        # Post-transaction processing (data transformation)
        item_dtos = [ItemPublic.model_validate(item) for item in items_from_db]

        return Paginated.create(
            items=item_dtos, total=total_count, params=query.page_params
        )
