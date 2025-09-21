import uuid
from pydantic import BaseModel
from app.shared.application.exceptions import ResourceNotFoundError
from app.features.iam.schemas import UserUpdateAdmin, UserPublic
from app.features.iam.infra.user_repository import UserRepository
from app.shared.infrastructure.uow import IUnitOfWork


class UpdateUserAdminCommand(BaseModel):
    user_id_to_update: uuid.UUID
    update_data: UserUpdateAdmin


class UpdateUserAdminHandler:
    def __init__(self, uow: IUnitOfWork):
        self.uow = uow

    async def handle(self, command: UpdateUserAdminCommand) -> UserPublic:
        async with self.uow:
            repo = self.uow.get_repository(UserRepository)

            db_user = await repo.get(command.user_id_to_update)
            if not db_user:
                raise ResourceNotFoundError("User not found.")

            # 注意：密码更新逻辑应该更复杂，需要操作IdentityRepository，这里是简化版
            updated_user = await repo.update_by_admin(
                db_user=db_user, user_in=command.update_data
            )
        return UserPublic.model_validate(updated_user)
