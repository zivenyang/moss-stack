import uuid
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from ..domain.user import User, UserCreate
from ..infra.security import get_password_hash

class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_username(self, username: str) -> User | None:
        statement = select(User).where(User.username == username)
        result = await self.session.exec(statement)
        return result.first()

    async def get_by_email(self, email: str) -> User | None:
        statement = select(User).where(User.email == email)
        result = await self.session.exec(statement)
        return result.first()

    async def get(self, user_id: uuid.UUID) -> User | None:
        return await self.session.get(User, user_id)

    async def create(self, user_in: UserCreate) -> User:
        hashed_password = get_password_hash(user_in.password)
        
        # 使用 model_dump 排除 password 字段
        user_data = user_in.model_dump(exclude={"password"})
        
        db_user = User(**user_data, hashed_password=hashed_password)
        
        self.session.add(db_user)
        await self.session.commit()
        await self.session.refresh(db_user)
        return db_user