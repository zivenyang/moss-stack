from fastapi import APIRouter, Depends, HTTPException, status
from app.shared.web.deps import get_current_active_user, get_uow
from app.features.iam.application.user.commands.update_profile import (
    UpdateProfileCommand,
    UpdateProfileHandler,
)
from app.shared.infrastructure.uow import IUnitOfWork
from ..schemas import UserPublic, UserUpdateProfile
from ..domain.user import User

router = APIRouter()


@router.get("/me", response_model=UserPublic)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user


@router.put("/me", response_model=UserPublic)
async def update_user_me(
    profile_data: UserUpdateProfile,
    current_user: User = Depends(get_current_active_user),
    uow: IUnitOfWork = Depends(get_uow),
):
    """
    Update current user's profile.
    """
    command = UpdateProfileCommand(user_id=current_user.id, profile_data=profile_data)
    handler = UpdateProfileHandler(uow)
    try:
        updated_user = await handler.handle(command)
        return updated_user
    except Exception as e:
        # This can be handled by a global exception middleware
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
