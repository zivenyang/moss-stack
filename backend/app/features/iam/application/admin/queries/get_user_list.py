from pydantic import BaseModel
from app.shared.infrastructure.uow import IUnitOfWork
from app.shared.schemas import Paginated, PageParams
from app.features.iam.schemas import UserInDBAdmin
from app.features.iam.infra.user_repository import UserRepository

class GetUserListAdminQuery(BaseModel):
    page_params: PageParams

class GetUserListAdminHandler:
    def __init__(self, uow: IUnitOfWork):
        self.uow = uow

    async def handle(self, query: GetUserListAdminQuery) -> Paginated[UserInDBAdmin]:
        users_from_db = []
        total_count = 0
        
        async with self.uow:
            repo = self.uow.get_repository(UserRepository)
            users_from_db, total_count = await repo.get_multi_paginated(
                skip=query.page_params.offset,
                limit=query.page_params.size
            )
        
        # --- Post-transaction processing ---
        user_dtos = [UserInDBAdmin.model_validate(user) for user in users_from_db]
        
        return Paginated.create(
            items=user_dtos,
            total=total_count,
            params=query.page_params
        )