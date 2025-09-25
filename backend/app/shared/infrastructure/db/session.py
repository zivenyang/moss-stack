from typing import AsyncGenerator
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from app.config import settings
from app.shared.infrastructure.logging.config import get_logger

logger = get_logger(__name__)

# 1. 创建异步引擎
# The DATABASE_URL from settings should already be in the async format
# e.g., "postgresql+asyncpg://user:password@host/db"
async_engine = create_async_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    echo=settings.DB_ECHO,
)

# 2. 创建异步会话工厂
AsyncSessionFactory = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# 3. 创建FastAPI依赖项，用于获取DB会话
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    The single dependency for getting a database session.
    It is responsible for the entire session lifecycle, including
    transaction management (commit/rollback) for a single request.
    """
    session: AsyncSession | None = None
    try:
        session = AsyncSessionFactory()
        yield session
        # If no exception was raised during the request, commit the transaction.
        await session.commit()
    except Exception:
        logger.exception("An exception occurred during the request. Rolling back transaction.")
        if session:
            await session.rollback()
        # Re-raise the exception to be handled by exception middleware
        raise
    finally:
        if session:
            await session.close()