from pydantic import BaseModel
from app.shared.infrastructure.uow import IUnitOfWork
from app.shared.domain.exceptions import BusinessRuleViolationError

# Import concrete repository classes to use as keys for the factory
from app.features.iam.infra.user_repository import UserRepository
from app.features.iam.infra.identity_repository import IdentityRepository

# Import DTOs and other necessary components
from app.features.iam.schemas import UserCreate, UserPublic


class RegisterUserCommand(BaseModel):
    user_data: UserCreate


class RegisterUserHandler:
    def __init__(self, uow: IUnitOfWork):
        self.uow = uow

    async def handle(self, command: RegisterUserCommand) -> UserPublic:
        async with self.uow:
            # Get repositories on-demand from the UoW factory
            user_repo = self.uow.get_repository(UserRepository)
            identity_repo = self.uow.get_repository(IdentityRepository)

            # Perform business logic checks
            if await user_repo.get_by_email(command.user_data.email):
                raise BusinessRuleViolationError("Email already registered.")
            if await user_repo.get_by_username(command.user_data.username):
                raise BusinessRuleViolationError("Username already exists.")

            # Create user (adds to session)
            new_user = await user_repo.create(user_in=command.user_data)

            # Flush to get the database-generated ID
            await self.uow.session.flush([new_user])

            # Create associated identities (adds to session)
            await identity_repo.create_password_identity(
                user_id=new_user.id,
                identifier=command.user_data.email,
                password=command.user_data.password,
            )
            await identity_repo.create_password_identity(
                user_id=new_user.id,
                identifier=command.user_data.username,
                password=command.user_data.password,
            )
            # The UoW will commit automatically when the 'with' block exits.

        return UserPublic.model_validate(new_user)
