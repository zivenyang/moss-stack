import uuid
from pydantic import BaseModel
from app.shared.infrastructure.uow import IUnitOfWork
from app.features.item.schemas import ItemPublic
from app.features.item.infra.item_repository import ItemRepository
from app.shared.schemas import PageParams, Paginated

class GetItemListQuery(BaseModel):
    owner_id: uuid.UUID
    page_params: PageParams

class GetItemListHandler:
    def __init__(self, uow: IUnitOfWork):
        self.uow = uow

    async def handle(self, query: GetItemListQuery) -> Paginated[ItemPublic]:
        items_from_db = []
        total_count = 0

        async with self.uow:
            repo = self.uow.get_repository(ItemRepository)
            items_from_db, total_count = await repo.get_multi_by_owner_paginated(
                owner_id=query.owner_id,
                offset=query.page_params.offset,
                limit=query.page_params.size
            )
        
        item_dtos = [ItemPublic.model_validate(item) for item in items_from_db]
        
        return Paginated.create(
            items=item_dtos,
            total=total_count,
            params=query.page_params
        )