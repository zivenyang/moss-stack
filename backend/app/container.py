from dependency_injector import containers, providers
from app.shared.infrastructure.db.session import AsyncSessionFactory
from app.shared.infrastructure.bus.event import (
    IEventBus,
    KafkaEventBus,
)  # Or KafkaEventBus
from app.shared.infrastructure.uow import IUnitOfWork, UnitOfWork


class AppContainer(containers.DeclarativeContainer):
    """
    The main dependency injection container for the application.
    It wires together all services and dependencies.
    """

    # --- Gateways / Configuration ---
    # This section holds providers for external services or config
    config = providers.Configuration()

    # --- Infrastructure Layer ---

    # Event Bus: Singleton provider, one instance for the entire app lifecycle.
    event_bus: providers.Singleton[IEventBus] = providers.Singleton(KafkaEventBus)

    session_factory_provider = providers.Object(AsyncSessionFactory)

    # Unit of Work: Factory provider, creates a new UoW instance for each request.
    uow: providers.Factory[IUnitOfWork] = providers.Factory(
        UnitOfWork,
        session_factory=session_factory_provider,
        event_bus=event_bus,
    )
