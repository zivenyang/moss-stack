import uuid
from typing import TYPE_CHECKING, List, Optional
from sqlmodel import Field, Relationship
from app.shared.domain.aggregate_root import AggregateRoot
from app.shared.domain.exceptions import BusinessRuleViolationError

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

    identities: List["Identity"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )

    # --- Business Methods ---
    def deactivate(self) -> None:
        if not self.is_active:
            raise BusinessRuleViolationError("User is already inactive.")
        self.is_active = False
        # self._add_domain_event(UserDeactivated(user_id=self.id))

    def activate(self) -> None:
        if self.is_active:
            raise BusinessRuleViolationError("User is already active.")
        self.is_active = True
        # self._add_domain_event(UserActivated(user_id=self.id))