from typing import List
from .entity import Entity
from .event import DomainEvent

class AggregateRoot(Entity):
    """
    Base class for aggregate roots.
    This version uses a standard instance attribute for domain events, initialized
    in a way that is compatible with both direct instantiation and ORM loading.
    """
    
    # We will not use PrivateAttr as it's not reliably initialized by SQLModel's loader.
    # Instead, we will use a standard attribute and ensure its initialization.
    
    # We use a double underscore to indicate it's a private, internal state.
    # We can't initialize it here, as it would be a class attribute.
    # __domain_events: List[DomainEvent] = [] # This is WRONG

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # This will be called when we create a new object in code, e.g., Item.create()
        self.__domain_events: List[DomainEvent] = []
        
    @property
    def domain_events(self) -> List[DomainEvent]:
        # Provide a fallback for objects loaded from DB that might have missed __init__
        if not hasattr(self, "__domain_events"):
            self.__domain_events: List[DomainEvent] = []
        return self.__domain_events

    def _add_domain_event(self, domain_event: DomainEvent):
        # The same fallback ensures the list exists before appending
        if not hasattr(self, "__domain_events"):
            self.__domain_events: List[DomainEvent] = []
        self.__domain_events.append(domain_event)

    def clear_domain_events(self) -> None:
        if hasattr(self, "__domain_events"):
            self.__domain_events.clear()