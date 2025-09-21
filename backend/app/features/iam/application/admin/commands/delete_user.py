import uuid
from pydantic import BaseModel
from app.shared.application.exceptions import ResourceNotFoundError
from app.shared.domain.exceptions import BusinessRuleViolationError
from app.features.iam.infra.user_repository import UserRepository
from app.shared.infrastructure.uow import IUnitOfWork


class DeleteUserAdminCommand(BaseModel):
    user_id_to_delete: uuid.UUID
    current_admin_id: uuid.UUID


class DeleteUserAdminHandler:
    def __init__(self, uow: IUnitOfWork):
        self.uow = uow

    async def handle(self, command: DeleteUserAdminCommand) -> None:
        async with self.uow:
            repo = self.uow.get_repository(UserRepository)
            if command.user_id_to_delete == command.current_admin_id:
                raise BusinessRuleViolationError("Admins cannot delete themselves.")

            db_user = await repo.get(command.user_id_to_delete)
            if not db_user:
                raise ResourceNotFoundError("User not found.")

            await repo.remove(db_user=db_user)
