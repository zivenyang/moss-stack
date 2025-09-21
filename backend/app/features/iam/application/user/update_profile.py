import uuid
from pydantic import BaseModel
from app.shared.infrastructure.uow import IUnitOfWork
from app.shared.application.exceptions import ResourceNotFoundError
from app.features.iam.schemas import UserUpdateProfile, UserPublic
from app.features.iam.infra.user_repository import UserRepository

class UpdateProfileCommand(BaseModel):
    user_id: uuid.UUID
    profile_data: UserUpdateProfile

class UpdateProfileHandler:
    def __init__(self, uow: IUnitOfWork):
        self.uow = uow

    async def handle(self, command: UpdateProfileCommand) -> UserPublic:
        async with self.uow:
            user_repo = self.uow.get_repository(UserRepository)
            db_user = await user_repo.get(command.user_id)
            if not db_user:
                raise ResourceNotFoundError("User not found.")
            
            updated_user = await user_repo.update_profile(
                db_user=db_user, user_in=command.profile_data
            )
        return UserPublic.model_validate(updated_user)
        