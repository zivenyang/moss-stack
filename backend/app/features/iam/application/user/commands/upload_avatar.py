import uuid
from pathlib import Path
from fastapi import UploadFile
from pydantic import BaseModel
from app.shared.infrastructure.uow import IUnitOfWork
from app.shared.infrastructure.storage.interface import IFileStorage
from app.features.iam.infra.user_repository import UserRepository
from app.features.iam.schemas import UserPublic
from app.config import settings


class UploadAvatarCommand(BaseModel):
    user_id: uuid.UUID
    file: UploadFile


class UploadAvatarHandler:
    def __init__(self, uow: IUnitOfWork, storage: IFileStorage):
        self.uow = uow
        self.storage = storage

    async def handle(self, command: UploadAvatarCommand) -> UserPublic:
        async with self.uow:
            repo = self.uow.get_repository(UserRepository)
            user = await repo.get(command.user_id)
            if not user:
                # This should be caught by authentication, but as a safeguard:
                raise Exception("User not found during avatar upload.")

            # Define path and filename
            file_extension = (
                Path(command.file.filename).suffix if command.file.filename else ".jpg"
            )
            path = f"avatars/{user.id}"
            filename = f"profile{file_extension}"

            # Delete old avatar if it exists
            if user.profile_picture_url:
                old_relative_path = user.profile_picture_url.replace(
                    settings.STATIC_URL + "/", ""
                )
                await self.storage.delete(old_relative_path)

            # Save the new file
            relative_path = await self.storage.save(
                file=command.file, path=path, filename=filename
            )

            # Update user's profile picture URL
            public_url = self.storage.get_public_url(relative_path)
            user.profile_picture_url = public_url

            # The UoW will commit the change to the user model

        return UserPublic.model_validate(user)
