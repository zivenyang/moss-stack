# backend/app/features/item/api.py

import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.shared.infrastructure.db.session import get_db_session
from app.shared.web.deps import get_current_active_user
from app.features.auth.domain.user import User

# Import all DTOs and Handlers
from .domain.item import ItemCreate, ItemPublic, ItemUpdate
from .commands.create_item import CreateItemCommand, CreateItemHandler
from .queries.get_items import GetItemsQuery, GetItemsHandler
from .commands.update_item import UpdateItemCommand, UpdateItemHandler
from .commands.delete_item import DeleteItemCommand, DeleteItemHandler
from .queries.get_item import GetItemQuery, GetItemHandler

router = APIRouter(prefix="/items")

# --- POST / (Create Item) - Already implemented ---
@router.post("", response_model=ItemPublic, status_code=status.HTTP_201_CREATED)
async def create_item(
    item_in: ItemCreate,
    session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
):
    command = CreateItemCommand(item_in=item_in, owner_id=current_user.id)
    handler = CreateItemHandler(session)
    item = await handler.handle(command)
    return item

# --- GET / (Read Items) - Already implemented ---
@router.get("", response_model=List[ItemPublic])
async def read_items(
    skip: int = 0,
    limit: int = 100,
    session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
):
    query = GetItemsQuery(owner_id=current_user.id, skip=skip, limit=limit)
    handler = GetItemsHandler(session)
    items = await handler.handle(query)
    return items

# --- GET /{item_id} (Read Item) - New ---
@router.get("/{item_id}", response_model=ItemPublic)
async def read_item(
    item_id: uuid.UUID,
    session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
):
    query = GetItemQuery(owner_id=current_user.id, item_id=item_id)
    handler = GetItemHandler(session)
    item = await handler.handle(query)
    return item

# --- PUT /{item_id} (Update Item) - New ---
@router.put("/{item_id}", response_model=ItemPublic)
async def update_item(
    item_id: uuid.UUID,
    item_in: ItemUpdate,
    session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
):
    """
    Update an item owned by the current user.
    """
    command = UpdateItemCommand(item_id=item_id, item_in=item_in, owner_id=current_user.id)
    handler = UpdateItemHandler(session)
    result = await handler.handle(command)

    if not result.is_success:
        # ResourceNotFoundError should translate to 404
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=result.error.message)
    
    return result.get_value()

# --- DELETE /{item_id} (Delete Item) - New ---
@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(
    item_id: uuid.UUID,
    session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
) -> None:
    """
    Delete an item owned by the current user.
    """
    command = DeleteItemCommand(item_id=item_id, owner_id=current_user.id)
    handler = DeleteItemHandler(session)
    result = await handler.handle(command)

    if not result.is_success:
        # ResourceNotFoundError should also translate to 404
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=result.error.message)

    # For 204 No Content, we should return nothing.
    return None