import uuid
from app.shared.domain.event import DomainEvent

class UserRegistered(DomainEvent):
    """
    Event published when a new user has successfully registered.
    """
    user_id: uuid.UUID
    username: str
    email: str