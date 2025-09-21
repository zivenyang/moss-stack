import abc
from typing import Self, Type, Dict, TypeVar
from sqlmodel.ext.asyncio.session import AsyncSession
from app.shared.infrastructure.db.session import AsyncSessionFactory

# Generic TypeVar for repositories
T = TypeVar("T")

class IUnitOfWork(abc.ABC):
    """
    Interface for the Unit of Work pattern.
    Defines the contract for managing transactions and providing repositories.
    """
    session: AsyncSession

    async def __aenter__(self) -> Self:
        raise NotImplementedError

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        raise NotImplementedError
    
    @abc.abstractmethod
    def get_repository(self, repo_type: Type[T]) -> T:
        raise NotImplementedError

class UnitOfWork(IUnitOfWork):
    """
    A Unit of Work that manages the database transaction and acts as a factory
    for repository instances. It ensures all repositories within a single
    unit of work share the same database session.
    """
    def __init__(self, session_factory):
        self._session_factory = session_factory
        self._session: AsyncSession | None = None
        self._repositories: Dict[Type, object] = {}

    async def __aenter__(self) -> Self:
        self.session = self._session_factory()
        self._repositories = {}  # Clear repositories for each new transaction
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        if self.session:
            if exc_type:
                await self.session.rollback()
            else:
                await self.session.commit()
            await self.session.close()

    def get_repository(self, repo_type: Type[T]) -> T:
        """
        Gets a repository instance for the given repository class.
        It lazily instantiates the repository on first access and caches it
        for the lifetime of the unit of work.
        
        :param repo_type: The class of the repository to get (e.g., UserRepository).
        :return: An instance of the requested repository.
        """
        if self.session is None:
            raise RuntimeError("Unit of Work is not active. Use within 'async with'.")

        if repo_type not in self._repositories:
            # Instantiate the repository class, passing the shared session to it.
            self._repositories[repo_type] = repo_type(self.session)
        
        # We know the type is correct, so we can safely cast it.
        return self._repositories[repo_type]