import abc
from typing import Self, Type, Dict, TypeVar
from sqlmodel.ext.asyncio.session import AsyncSession

from app.shared.infrastructure.bus.event import IEventBus
from app.shared.domain.aggregate_root import AggregateRoot

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

    def __init__(self, session_factory, event_bus: IEventBus):
        self._session_factory = session_factory
        self._event_bus = event_bus
        self._session: AsyncSession | None = None
        self._repositories: Dict[Type, object] = {}
        self._tracked_aggregates: set[AggregateRoot] = set()

    def track(self, aggregate: AggregateRoot):
        """
        Adds an aggregate to the tracked list. The UoW will collect and publish
        domain events from tracked aggregates upon successful commit.
        """
        self._tracked_aggregates.add(aggregate)

    async def __aenter__(self) -> Self:
        self.session = self._session_factory()
        self._repositories = {}
        self._tracked_aggregates = set()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            if exc_type:
                await self.session.rollback()
            else:
                await self.session.commit()
                # Event publishing is now an integral part of the UoW's responsibility.
                await self._publish_events()
            await self.session.close()

    async def _publish_events(self):
        """Collects and publishes domain events from all tracked aggregates."""
        events_to_publish = []
        for aggregate in self._tracked_aggregates:
            events_to_publish.extend(aggregate.domain_events)
            aggregate.clear_domain_events()
        
        if events_to_publish:
            self._event_bus.publish(events_to_publish)

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
