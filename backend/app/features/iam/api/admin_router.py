import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from app.shared.web.deps import get_current_active_superuser, get_uow
from app.shared.infrastructure.uow import IUnitOfWork
from app.features.iam.application.admin.get_user_list import GetUserListAdminHandler, GetUserListAdminQuery
from app.features.iam.application.admin.get_user_by_id import GetUserByIdAdminHandler, GetUserByIdAdminQuery
from app.shared.application.exceptions import ResourceNotFoundError
from ..domain.user import User
from ..schemas import UserInDBAdmin, UserUpdateAdmin, UserPublic
from ..application.admin.update_user import UpdateUserAdminCommand, UpdateUserAdminHandler
from ..application.admin.delete_user import DeleteUserAdminCommand, DeleteUserAdminHandler

router = APIRouter()

@router.get("/", response_model=List[UserInDBAdmin])
async def read_users_admin(
    skip: int = 0, limit: int = 100,
    uow: IUnitOfWork = Depends(get_uow),
    current_user: User = Depends(get_current_active_superuser),
):
    """
    Retrieve all users (for admins).
    """
    query = GetUserListAdminQuery(skip=skip, limit=limit)
    handler = GetUserListAdminHandler(uow)
    return await handler.handle(query)

@router.get("/{user_id}", response_model=UserInDBAdmin)
async def read_user_by_id_admin(
    user_id: uuid.UUID,
    uow: IUnitOfWork = Depends(get_uow),
    current_user: User = Depends(get_current_active_superuser),
):
    """
    Get a specific user by ID (for admins).
    """
    query = GetUserByIdAdminQuery(user_id=user_id)
    handler = GetUserByIdAdminHandler(uow)
    try:
        return await handler.handle(query)
    except ResourceNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.put("/{user_id}", response_model=UserPublic)
async def update_user_admin(
    user_id: uuid.UUID,
    user_in: UserUpdateAdmin,
    uow: IUnitOfWork = Depends(get_uow),
    current_user: User = Depends(get_current_active_superuser),
):
    """
    Update a user's information by admin.
    """
    command = UpdateUserAdminCommand(user_id_to_update=user_id, update_data=user_in)
    handler = UpdateUserAdminHandler(uow)
    try:
        return await handler.handle(command)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_admin(
    user_id: uuid.UUID,
    uow: IUnitOfWork = Depends(get_uow),
    current_user: User = Depends(get_current_active_superuser),
) -> None:
    """
    Delete a user by admin.
    """
    command = DeleteUserAdminCommand(
        user_id_to_delete=user_id,
        current_admin_id=current_user.id,
    )
    handler = DeleteUserAdminHandler(uow)
    try:
        await handler.handle(command)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))