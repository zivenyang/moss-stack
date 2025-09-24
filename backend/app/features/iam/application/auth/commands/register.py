from pydantic import BaseModel
from app.shared.infrastructure.uow import IUnitOfWork
from app.shared.domain.exceptions import BusinessRuleViolationError

# Import concrete repository classes to use as keys for the factory
from app.features.iam.infra.user_repository import UserRepository
from app.features.iam.infra.identity_repository import IdentityRepository

# Import DTOs and other necessary components
from app.features.iam.schemas import UserCreate, UserPublic
from app.features.iam.domain.user import User
from app.shared.application.interfaces import ICommandHandler


class RegisterUserCommand(BaseModel):
    user_data: UserCreate


class RegisterUserHandler(ICommandHandler[RegisterUserCommand, UserPublic]):
    def __init__(self, uow: IUnitOfWork):
        self.uow = uow

    async def handle(self, command: RegisterUserCommand) -> UserPublic:
        email_lower = command.user_data.email.lower()
        username_lower = command.user_data.username.lower()

        async with self.uow:
            user_repo = self.uow.get_repository(UserRepository)
            identity_repo = self.uow.get_repository(IdentityRepository)

            if await user_repo.get_by_email(email_lower):
                raise BusinessRuleViolationError("Email already registered.")
            if await user_repo.get_by_username(username_lower):
                raise BusinessRuleViolationError("Username already exists.")

            new_user = User.register(username=username_lower, email=email_lower)
            self.uow.track(new_user)
            user_repo.add(new_user)
            await self.uow.session.flush([new_user])

            await identity_repo.create_password_identity(
                user_id=new_user.id,
                identifier=email_lower,
                password=command.user_data.password,
            )
            await identity_repo.create_password_identity(
                user_id=new_user.id,
                identifier=username_lower,
                password=command.user_data.password,
            )

        return UserPublic.model_validate(new_user)
