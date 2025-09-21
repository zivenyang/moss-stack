import uuid
from typing import Optional
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from ..domain.identity import Identity, IdentityProvider
from .security import get_password_hash

class IdentityRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_provider(self, provider: IdentityProvider, provider_user_id: str) -> Optional[Identity]:
        statement = select(Identity).where(
            Identity.provider == provider,
            Identity.provider_user_id == provider_user_id
        )
        return (await self.session.exec(statement)).first()

    async def create_password_identity(
        self, user_id: uuid.UUID, identifier: str, password: str
    ) -> Identity:
        hashed_password = get_password_hash(password)
        db_identity = Identity(
            user_id=user_id,
            provider=IdentityProvider.PASSWORD,
            provider_user_id=identifier,
            credentials=hashed_password,
        )
        self.session.add(db_identity)
        return db_identity