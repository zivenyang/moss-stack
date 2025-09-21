import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from app.shared.infrastructure.uow import IUnitOfWork
from app.shared.web.deps import get_uow, get_current_active_superuser
from app.features.iam.domain.user import User
from app.features.item.application.admin.commands.delete_item import DeleteItemAdminCommand, DeleteItemAdminHandler
from app.features.item.application.admin.commands.update_item import UpdateItemAdminCommand, UpdateItemAdminHandler
from app.shared.application.exceptions import ResourceNotFoundError
from app.features.item.application.admin.queries.get_item_by_id import GetItemByIdAdminHandler, GetItemByIdAdminQuery

from ..schemas import ItemPublic, ItemUpdateAdmin
from app.features.item.application.admin.queries.get_all_items import GetAllItemsAdminQuery, GetAllItemsAdminHandler

router = APIRouter()

@router.get("/", response_model=List[ItemPublic])
async def read_items_admin(
    skip: int = 0, limit: int = 100,
    uow: IUnitOfWork = Depends(get_uow),
    current_user: User = Depends(get_current_active_superuser),
):
    query = GetAllItemsAdminQuery(skip=skip, limit=limit)
    handler = GetAllItemsAdminHandler(uow)
    return await handler.handle(query)

@router.get("/{item_id}", response_model=ItemPublic)
async def read_item_admin(
    item_id: uuid.UUID,
    uow: IUnitOfWork = Depends(get_uow),
    current_user: User = Depends(get_current_active_superuser),
):
    """
    Get any item in the system by its ID. (Admin access required)
    """
    query = GetItemByIdAdminQuery(item_id=item_id)
    handler = GetItemByIdAdminHandler(uow)
    try:
        return await handler.handle(query)
    except ResourceNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.put("/{item_id}", response_model=ItemPublic)
async def update_item_admin(
    item_id: uuid.UUID,
    item_in: ItemUpdateAdmin,
    uow: IUnitOfWork = Depends(get_uow),
    current_user: User = Depends(get_current_active_superuser),
):
    """
    Update any item in the system. (Admin access required)
    """
    command = UpdateItemAdminCommand(item_id=item_id, item_in=item_in)
    handler = UpdateItemAdminHandler(uow)
    try:
        return await handler.handle(command)
    except ResourceNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item_admin(
    item_id: uuid.UUID,
    uow: IUnitOfWork = Depends(get_uow),
    current_user: User = Depends(get_current_active_superuser),
) -> None:
    """
    Delete any item in the system. (Admin access required)
    """
    command = DeleteItemAdminCommand(item_id=item_id)
    handler = DeleteItemAdminHandler(uow)
    try:
        await handler.handle(command)
    except ResourceNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))