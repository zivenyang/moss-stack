from pydantic import BaseModel
from app.shared.infrastructure.uow import IUnitOfWork
from app.shared.schemas import Paginated, PageParams
from app.features.item.schemas import ItemPublic
from app.features.item.infra.item_repository import ItemRepository

class GetAllItemsAdminQuery(BaseModel):
    page_params: PageParams

class GetAllItemsAdminHandler:
    def __init__(self, uow: IUnitOfWork):
        self.uow = uow

    async def handle(self, query: GetAllItemsAdminQuery) -> Paginated[ItemPublic]:
        items_from_db = []
        total_count = 0

        async with self.uow:
            repo = self.uow.get_repository(ItemRepository)
            items_from_db, total_count = await repo.get_multi_admin_paginated(
                skip=query.page_params.offset,
                limit=query.page_params.size
            )

        # --- Post-transaction processing ---
        item_dtos = [ItemPublic.model_validate(item) for item in items_from_db]
        
        return Paginated.create(
            items=item_dtos,
            total=total_count,
            params=query.page_params
        )