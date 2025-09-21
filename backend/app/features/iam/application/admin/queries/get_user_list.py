from typing import List
from pydantic import BaseModel
from app.shared.infrastructure.uow import IUnitOfWork
from app.features.iam.schemas import UserInDBAdmin
from app.features.iam.infra.user_repository import UserRepository

class GetUserListAdminQuery(BaseModel):
    skip: int = 0
    limit: int = 100

class GetUserListAdminHandler:
    def __init__(self, uow: IUnitOfWork):
        self.uow = uow

    async def handle(self, query: GetUserListAdminQuery) -> List[UserInDBAdmin]:
        # 对于只读操作，使用事务不是必须的，但通过UoW获取session可以保持一致性
        async with self.uow:
            repo = self.uow.get_repository(UserRepository)
            users = await repo.get_multi(skip=query.skip, limit=query.limit)
            # 转换为DTO
            return [UserInDBAdmin.model_validate(user) for user in users]