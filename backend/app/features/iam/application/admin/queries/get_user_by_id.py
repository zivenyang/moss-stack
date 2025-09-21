import uuid
from pydantic import BaseModel
from app.shared.infrastructure.uow import IUnitOfWork
from app.shared.application.exceptions import ResourceNotFoundError
from app.features.iam.schemas import UserInDBAdmin
from app.features.iam.infra.user_repository import UserRepository

class GetUserByIdAdminQuery(BaseModel):
    user_id: uuid.UUID

class GetUserByIdAdminHandler:
    def __init__(self, uow: IUnitOfWork):
        self.uow = uow

    async def handle(self, query: GetUserByIdAdminQuery) -> UserInDBAdmin:
        async with self.uow:
            repo = self.uow.get_repository(UserRepository)
            user = await repo.get(query.user_id)
            if not user:
                raise ResourceNotFoundError("User not found.")
            return UserInDBAdmin.model_validate(user)