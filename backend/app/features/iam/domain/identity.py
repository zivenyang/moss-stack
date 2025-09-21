import uuid
from enum import Enum
from typing import TYPE_CHECKING, Optional
from sqlmodel import Field, Relationship
from app.shared.domain.entity import Entity

if TYPE_CHECKING:
    from .user import User


class IdentityProvider(str, Enum):
    """Enumeration for different authentication providers."""
    PASSWORD = "password"
    GOOGLE = "google"
    GITHUB = "github"
    LDAP = "ldap"

class Identity(Entity, table=True):
    """
    Represents a specific authentication credential for a user.
    A single User can have multiple Identities (e.g., password, Google, etc.).
    This table is the core of the Identity/Entity separation pattern.
    """
    # The 'id' is inherited from Entity.
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, nullable=False)
    
    # Foreign key to the User aggregate root.
    user_id: uuid.UUID = Field(foreign_key="user.id", index=True)
    user: Optional["User"] = Relationship(back_populates="identities")
    
    # The authentication provider.
    provider: IdentityProvider = Field(index=True)
    
    # The user's unique identifier within the provider's system.
    # For 'password', this is the username or email.
    # For 'google', this is the 'sub' claim.
    provider_user_id: str = Field(index=True)
    
    # The credentials for this identity, if applicable.
    # For 'password', this stores the hashed password.
    # For OAuth2 providers, this can be null.
    credentials: Optional[str] = None