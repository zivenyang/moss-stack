# backend/app/features/auth/domain/user.py

import uuid
from sqlmodel import Field, SQLModel
from app.shared.domain.aggregate_root import AggregateRoot
from app.shared.domain.exceptions import BusinessRuleViolationError

# --- Data Transfer & Base Model ---
# This defines the common fields for the User aggregate.
# It's a plain SQLModel, not a table model.
class UserBase(SQLModel):
    username: str = Field(index=True, unique=True, max_length=50)
    email: str = Field(unique=True, index=True, max_length=100)
    is_active: bool = Field(default=True)
    is_superuser: bool = Field(default=False)


# --- The Aggregate Root ---
# This is the core domain model AND the database table model.
# It inherits from AggregateRoot, UserBase, and sets table=True.
class User(AggregateRoot, UserBase, table=True):
    # The 'id' field is inherited from AggregateRoot -> Entity.
    # We override it here only to add specific database constraints like nullable=False.
    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        nullable=False,
        description="The unique identifier for the user."
    )
    hashed_password: str = Field(nullable=False)

    # --- Business Methods (Domain Logic) ---
    def deactivate(self) -> None:
        """
        Deactivates the user. This is an example of a business method
        that enforces a domain rule.
        """
        if not self.is_active:
            raise BusinessRuleViolationError("User is already inactive.")
        self.is_active = False
        # Example of adding a domain event after a state change:
        # self._add_domain_event(UserDeactivated(user_id=self.id))

    def activate(self) -> None:
        """Activates the user."""
        if self.is_active:
            raise BusinessRuleViolationError("User is already active.")
        self.is_active = True
        # self._add_domain_event(UserActivated(user_id=self.id))


# --- Pydantic-only Models for API Operations ---

# Used for creating a new user via the API.
# It includes the plaintext password which should never be stored.
class UserCreate(UserBase):
    password: str = Field(min_length=8)

# Used for exposing user data to the public via the API.
# It safely exposes the ID and other public fields, but not the hashed_password.
class UserPublic(UserBase):
    id: uuid.UUID