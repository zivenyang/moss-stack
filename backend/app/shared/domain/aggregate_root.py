from typing import List
from .entity import Entity
from .event import DomainEvent

class AggregateRoot(Entity):
    """
    The base class for aggregate roots in our pure domain model.
    
    It inherits from Entity, giving it a unique identifier, and adds the
    critical responsibility of managing domain events.
    
    The event list is a standard instance attribute, reliably initialized
    by Pydantic's standard constructor, ensuring that every aggregate
    instance has its own independent list of events. This class has zero
    dependencies on any infrastructure frameworks like SQLAlchemy or SQLModel.
    """

    # We use a standard Pydantic field definition.
    # - `default_factory=list`: Ensures a new list is created for each new instance.
    # - `private=True`: In Pydantic v1 style, or just convention. In Pydantic v2,
    #   private attributes are handled differently, but a simple leading underscore
    #   is a strong convention for a non-public, internal state.
    #   We will manage it as a regular instance attribute initialized in __init__.
    
    _domain_events: List[DomainEvent]

    def __init__(self, **data):
        """
        Custom initializer that ensures the domain events list is always present.
        Pydantic's BaseModel will call this.
        """
        super().__init__(**data)
        self._domain_events = []

    @property
    def domain_events(self) -> List[DomainEvent]:
        """Returns the list of recorded domain events for this aggregate."""
        return self._domain_events

    def _add_domain_event(self, domain_event: DomainEvent) -> None:
        """Adds a domain event to the aggregate's list of events."""
        self._domain_events.append(domain_event)

    def clear_domain_events(self) -> None:
        """
        Clears the list of domain events. Called by the Unit of Work after
        events have been successfully published.
        """
        self._domain_events.clear()