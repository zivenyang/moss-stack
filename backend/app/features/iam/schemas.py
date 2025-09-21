import uuid
from typing import Optional
from pydantic import BaseModel, EmailStr
from sqlmodel import SQLModel

# --- Token Schemas ---
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenPayload(BaseModel):
    sub: str # Subject (user_id)

# --- User Schemas for API ---
class UserBase(SQLModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserUpdateProfile(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None

class UserPublic(UserBase):
    id: uuid.UUID
    is_active: bool
    is_superuser: bool
    profile_picture_url: Optional[str] = None

# --- Admin Schemas ---
class UserInDBAdmin(UserPublic):
    # It inherits all fields from UserPublic:
    # id, username, email, is_active, is_superuser, profile_picture_url
    
    # In the future, you could add admin-only viewable fields here, for example:
    # last_login: Optional[datetime] = None
    # created_at: datetime
    pass

class UserUpdateAdmin(BaseModel):
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None
    password: Optional[str] = None