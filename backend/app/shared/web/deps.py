from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlmodel.ext.asyncio.session import AsyncSession

from app.config import settings
from app.features.iam.domain.user import User
from app.features.iam.infra.user_repository import UserRepository
from app.shared.infrastructure.db.session import get_db_session
from app.shared.infrastructure.uow import IUnitOfWork
from app.shared.infrastructure.storage.interface import IFileStorage
from app.shared.infrastructure.storage.local import LocalFileStorage
from dependency_injector.wiring import inject, Provide
from app.di import AppContainer

from app.shared.infrastructure.logging.config import get_logger
logger = get_logger(__name__)

# This points to our login endpoint
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/login/access-token"
)


async def get_current_user(
    token: str = Depends(oauth2_scheme), session: AsyncSession = Depends(get_db_session)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        user_id = payload.get("sub")
        logger.debug("Successfully decoded token", user_id=str(user_id))
        if user_id is None:
            raise credentials_exception
    except (JWTError, ValueError) as e:
        logger.warning("Token validation failed", error=str(e), token=token)
        raise credentials_exception

    repo = UserRepository(session)
    user = await repo.get(user_id)
    if user is None:
        logger.warning("User not found in DB for a valid token", user_id=str(user_id))
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def get_current_active_superuser(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """
    FastAPI dependency that requires the current user to be an active superuser.
    It builds upon the `get_current_active_user` dependency.
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges",
        )
    return current_user


@inject
def get_uow(
    uow: IUnitOfWork = Depends(Provide[AppContainer.uow]),
) -> IUnitOfWork:
    return uow


def get_file_storage() -> IFileStorage:
    """Dependency to get a file storage instance."""
    return LocalFileStorage(
        base_path=settings.STATIC_FILES_PATH, base_url=settings.STATIC_URL
    )
