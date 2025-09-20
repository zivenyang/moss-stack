# backend/app/shared/domain/aggregate_root.py

from typing import List
from .entity import Entity
from .event import DomainEvent

class AggregateRoot(Entity):
    """
    Base class for aggregate roots, inheriting from Entity.
    
    An aggregate root is a specific type of entity that acts as an entry point
    to a cluster of associated objects (the "aggregate"). It is the only object
    within the aggregate that external objects are allowed to hold references to.
    
    This class adds the capability to manage and dispatch domain events that occur
    within the aggregate, ensuring that business operations and their resulting
    events are managed transactionally.
    """
    _domain_events: List[DomainEvent] = []

    @property
    def domain_events(self) -> List[DomainEvent]:
        """
        Returns the list of recorded domain events that have occurred in this aggregate.
        """
        return self._domain_events

    def _add_domain_event(self, domain_event: DomainEvent) -> None:
        """
        Adds a domain event to the aggregate's list of events. This is an internal
        method intended to be called by the aggregate's business methods after a
        state change.
        """
        self._domain_events.append(domain_event)

    def clear_domain_events(self) -> None:
        """
        Clears the list of domain events. This should be called after the events
        have been successfully dispatched by the infrastructure layer (e.g., after
        a successful database commit).
        """
        self._domain_events.clear()