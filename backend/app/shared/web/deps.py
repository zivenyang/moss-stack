import uuid
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlmodel.ext.asyncio.session import AsyncSession
from dependency_injector.wiring import inject, Provide

from app.config import settings
from app.container import AppContainer # Import the container
from app.features.iam.domain.user import User
from app.features.iam.infra.user_repository import UserRepository
from app.shared.infrastructure.db.session import get_db_session # The one and only session provider
from app.shared.infrastructure.uow import IUnitOfWork, UnitOfWork
from app.shared.infrastructure.storage.interface import IFileStorage
from app.shared.infrastructure.storage.local import LocalFileStorage
from app.shared.infrastructure.logging.config import get_logger

logger = get_logger(__name__)

# OAuth2 scheme now points to the correct auth router prefix
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login/access-token"
)

# --- [核心修改] UoW Dependency ---
@inject
def get_uow(
    session: AsyncSession = Depends(get_db_session),
    # The event_bus is now injected from the container
    event_bus = Depends(Provide[AppContainer.event_bus]),
) -> IUnitOfWork:
    """
    Dependency that provides a Unit of Work instance.
    It receives the request-scoped session from `get_db_session`.
    It no longer manages transactions, only orchestrates repositories and events.
    """
    return UnitOfWork(session=session, event_bus=event_bus)

# --- User Authentication Dependencies ---
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    # It uses the exact same session provider as the UoW
    session: AsyncSession = Depends(get_db_session)
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
        user_id_str = payload.get("sub")
        if not user_id_str:
            raise credentials_exception
        user_id = uuid.UUID(user_id_str)
        logger.debug("Successfully decoded token", user_id=str(user_id))
    except (JWTError, ValueError):
        logger.warning("Token validation failed", exc_info=True)
        raise credentials_exception

    # The repository is created with the request-scoped session
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
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges",
        )
    return current_user

# --- Other Dependencies ---
def get_file_storage() -> IFileStorage:
    return LocalFileStorage(
        base_path=settings.STATIC_FILES_PATH, base_url=settings.STATIC_URL
    )