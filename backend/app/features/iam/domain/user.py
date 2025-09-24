import uuid
from typing import TYPE_CHECKING, List, Optional
from sqlmodel import Field, Relationship
from app.shared.domain.aggregate_root import AggregateRoot
from app.shared.domain.exceptions import BusinessRuleViolationError
from app.features.iam.domain.events import UserRegistered

if TYPE_CHECKING:
    from .identity import Identity


class User(AggregateRoot, table=True):
    """
    Represents the User aggregate root.
    This model holds the user's core profile information and business logic,
    but explicitly DOES NOT contain any authentication credentials like passwords.
    """

    # The 'id' is inherited from AggregateRoot -> Entity.
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, nullable=False)

    username: str = Field(index=True, unique=True, max_length=50)
    email: str = Field(unique=True, index=True, max_length=100)
    profile_picture_url: Optional[str] = None

    is_active: bool = Field(default=True)
    is_superuser: bool = Field(default=False)
    version: int = Field(default=0)

    identities: List["Identity"] = Relationship(
        back_populates="user", sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )

    # --- Business Methods ---
    @staticmethod
    def register(username: str, email: str) -> "User":
        user = User(username=username, email=email, version=1)
        user._add_domain_event(
            UserRegistered(user_id=user.id, username=user.username, email=user.email)
        )
        return user

    def deactivate(self):
        if not self.is_active:
            raise BusinessRuleViolationError("User is already inactive.")
        self.is_active = False
        # self._add_domain_event(...)

    def activate(self):
        if self.is_active:
            raise BusinessRuleViolationError("User is already active.")
        self.is_active = True
        # self._add_domain_event(...)