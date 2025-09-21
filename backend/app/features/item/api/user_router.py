import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from app.shared.infrastructure.uow import IUnitOfWork
from app.shared.web.deps import get_uow, get_current_active_user
from app.features.iam.domain.user import User
from app.features.item.application.user.queries.get_item_by_id import (
    GetItemByIdHandler,
    GetItemByIdQuery,
)
from app.shared.application.exceptions import ResourceNotFoundError
from app.shared.schemas import PageParams, Paginated

from ..schemas import ItemCreate, ItemPublic
from ..application.user.commands.create_item import CreateItemCommand, CreateItemHandler
from ..application.user.queries.get_item_list import (
    GetItemListQuery,
    GetItemListHandler,
)

router = APIRouter()


@router.post("/", response_model=ItemPublic, status_code=201)
async def create_item(
    item_in: ItemCreate,
    uow: IUnitOfWork = Depends(get_uow),
    current_user: User = Depends(get_current_active_user),
):
    command = CreateItemCommand(item_in=item_in, owner_id=current_user.id)
    handler = CreateItemHandler(uow)
    return await handler.handle(command)


@router.get("/", response_model=Paginated[ItemPublic])
async def read_items(
    pagination: PageParams = Depends(),
    uow: IUnitOfWork = Depends(get_uow),
    current_user: User = Depends(get_current_active_user),
):
    """
    Retrieve a paginated list of items owned by the current user.
    """
    query = GetItemListQuery(owner_id=current_user.id, page_params=pagination)
    handler = GetItemListHandler(uow)
    return await handler.handle(query)


@router.get("/{item_id}", response_model=ItemPublic)
async def read_item(
    item_id: uuid.UUID,
    uow: IUnitOfWork = Depends(get_uow),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get an item by ID, owned by the current user.
    """
    query = GetItemByIdQuery(item_id=item_id, owner_id=current_user.id)
    handler = GetItemByIdHandler(uow)
    try:
        return await handler.handle(query)
    except ResourceNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
