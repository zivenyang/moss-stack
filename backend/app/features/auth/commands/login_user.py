from pydantic import BaseModel
from sqlmodel.ext.asyncio.session import AsyncSession
from app.shared.application.result import Result
from app.shared.application.exceptions import AuthorizationError
from ..schemas import LoginRequest, Token
from ..infra.user_repository import UserRepository
from ..infra.security import verify_password, create_access_token

class LoginUserCommand(BaseModel):
    login_data: LoginRequest

class LoginUserHandler:
    def __init__(self, session: AsyncSession):
        self.repo = UserRepository(session)

    async def handle(self, command: LoginUserCommand) -> Result[Token, AuthorizationError]:
        user = await self.repo.get_by_username(command.login_data.username)
        if not user or not verify_password(command.login_data.password, user.hashed_password):
            return Result.failure(AuthorizationError("Incorrect username or password."))

        if not user.is_active:
            return Result.failure(AuthorizationError("Inactive user."))

        access_token = create_access_token(subject=user.id)
        return Result.success(Token(access_token=access_token))