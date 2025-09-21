from pydantic import BaseModel
from app.features.iam.domain.identity import IdentityProvider
from app.features.iam.infra.identity_repository import IdentityRepository
from app.features.iam.infra.user_repository import UserRepository
from app.features.iam.infra.security import verify_password, create_access_token
from app.features.iam.schemas import Token
from app.shared.application.exceptions import AuthorizationError
from app.shared.infrastructure.uow import IUnitOfWork

class LoginCommand(BaseModel):
    identifier: str
    password: str

class LoginHandler:
    def __init__(self, uow: IUnitOfWork):
        self.uow = uow

    async def handle(self, command: LoginCommand) -> Token:
        async with self.uow:
            identity_repo = self.uow.get_repository(IdentityRepository)
            user_repo = self.uow.get_repository(UserRepository)

            identity = await identity_repo.get_by_provider(
                provider=IdentityProvider.PASSWORD,
                provider_user_id=command.identifier
            )
            if not identity or not identity.credentials or not verify_password(command.password, identity.credentials):
                raise AuthorizationError("Incorrect identifier or password.")

            user = await user_repo.get(identity.user_id)
            if not user or not user.is_active:
                raise AuthorizationError("User is inactive or not found.")

            access_token = create_access_token(subject=user.id)
        return Token(access_token=access_token)