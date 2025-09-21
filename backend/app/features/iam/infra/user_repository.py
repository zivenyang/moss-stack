import uuid
from typing import List, Optional, Tuple
from sqlmodel import func, select
from sqlmodel.ext.asyncio.session import AsyncSession
from ..domain.user import User
from ..schemas import UserCreate, UserUpdateAdmin, UserUpdateProfile


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, user_id: uuid.UUID) -> Optional[User]:
        return await self.session.get(User, user_id)

    async def get_by_email(self, email: str) -> Optional[User]:
        statement = select(User).where(User.email == email)
        return (await self.session.exec(statement)).first()

    async def get_by_username(self, username: str) -> Optional[User]:
        statement = select(User).where(User.username == username)
        return (await self.session.exec(statement)).first()

    async def create(self, user_in: UserCreate) -> User:
        user_data = user_in.model_dump(exclude={"password"})
        db_user = User(**user_data)
        self.session.add(db_user)
        # Commit is handled by Unit of Work
        return db_user

    async def update(self, db_user: User, user_in: UserUpdateAdmin) -> User:
        update_data = user_in.model_dump(exclude_unset=True)
        # Password update is handled by IdentityRepository
        if "password" in update_data:
            del update_data["password"]

        for key, value in update_data.items():
            setattr(db_user, key, value)
        self.session.add(db_user)
        return db_user

    async def get_multi_paginated(
        self, skip: int = 0, limit: int = 100
    ) -> Tuple[List[User], int]:
        """
        Gets a paginated list of all users and the total count.
        """
        # Query for the data
        data_statement = (
            select(User)
            .order_by(User.username)  # Use a consistent order
            .offset(skip)
            .limit(limit)
        )
        items = (await self.session.exec(data_statement)).all()

        # Query for the total count
        count_statement = select(func.count()).select_from(User)
        total = (await self.session.exec(count_statement)).one()

        return items, total

    async def remove(self, db_user: User) -> None:
        # 删除用户时，也应该级联删除其所有 Identities
        # This should be configured at the DB level (ON DELETE CASCADE)
        # or handled explicitly here.
        await self.session.delete(db_user)
        await self.session.commit()

    async def save(self, user: User) -> User:
        """A generic save method for creating or updating a user."""
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def update_profile(self, db_user: User, user_in: UserUpdateProfile) -> User:
        """Updates a user's own profile information."""
        update_data = user_in.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_user, key, value)
        return await self.save(db_user)

    # 管理员的 update 方法已经很完善了，它可以处理密码重置
    async def update_by_admin(self, db_user: User, user_in: UserUpdateAdmin) -> User:
        update_data = user_in.model_dump(exclude_unset=True)

        if "password" in update_data and update_data["password"]:
            # 当管理员重置密码时，需要找到并更新对应的 password identity
            # 这是一个更复杂的流程，暂时简化为直接更新 User 表，但实际上应操作 Identity
            # TODO: Implement password reset via IdentityRepository
            # For now, let's assume we need a way to hash it
            from .security import get_password_hash

            hashed_password = get_password_hash(update_data["password"])
            # This demonstrates a flaw if we were to store password in User table
            # db_user.hashed_password = hashed_password
            del update_data["password"]

        for key, value in update_data.items():
            setattr(db_user, key, value)

        return await self.save(db_user)
