from typing import List, TypeVar
from .event import DomainEvent
from .entity import Entity

T = TypeVar("T")

class AggregateRoot(Entity):
    """
    Base class for aggregate roots in the domain layer.
    An aggregate root is a specific type of entity that acts as an entry point
    to a cluster of associated objects (the "aggregate").
    It also manages a list of domain events that occurred within the aggregate.
    """
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._domain_events: List[DomainEvent] = []

    @property
    def domain_events(self) -> List[DomainEvent]:
        """Returns the list of recorded domain events."""
        return self._domain_events

    def _add_domain_event(self, domain_event: DomainEvent) -> None:
        """
        Adds a domain event to the aggregate's list of events.
        This is typically called by methods within the aggregate that
        perform business logic and result in a state change.
        """
        self._domain_events.append(domain_event)

    def clear_domain_events(self) -> None:
        """Clears the list of domain events."""
        self._domain_events.clear()