from pydantic import BaseModel
from sqlmodel.ext.asyncio.session import AsyncSession
from app.shared.application.result import Result
from app.shared.domain.exceptions import BusinessRuleViolationError
from ..domain.user import UserCreate, UserPublic
from ..infra.user_repository import UserRepository

class RegisterUserCommand(BaseModel):
    user_data: UserCreate

class RegisterUserHandler:
    def __init__(self, session: AsyncSession):
        self.repo = UserRepository(session)

    async def handle(self, command: RegisterUserCommand) -> Result[UserPublic, BusinessRuleViolationError]:
        existing_user = await self.repo.get_by_username(command.user_data.username)
        if existing_user:
            return Result.failure(BusinessRuleViolationError("Username already exists."))
        
        existing_email = await self.repo.get_by_email(command.user_data.email)
        if existing_email:
            return Result.failure(BusinessRuleViolationError("Email already registered."))

        new_user = await self.repo.create(command.user_data)
        return Result.success(UserPublic.model_validate(new_user))