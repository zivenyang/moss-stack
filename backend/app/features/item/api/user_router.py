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
from app.features.item.application.user.commands.update_item import (
    UpdateItemCommand,
    UpdateItemHandler,
)
from app.features.item.application.user.commands.delete_item import (
    DeleteItemCommand,
    DeleteItemHandler,
)
from app.shared.infrastructure.logging.config import get_logger

from ..schemas import ItemCreate, ItemPublic, ItemUpdate
from ..application.user.commands.create_item import CreateItemCommand, CreateItemHandler
from ..application.user.queries.get_item_list import (
    GetItemListQuery,
    GetItemListHandler,
)

logger = get_logger(__name__)

router = APIRouter(prefix="/items", tags=["Items"])


@router.post("", response_model=ItemPublic, status_code=201)
async def create_item(
    item_in: ItemCreate,
    uow: IUnitOfWork = Depends(get_uow),
    current_user: User = Depends(get_current_active_user),
):
    command = CreateItemCommand(item_in=item_in, owner_id=current_user.id)
    handler = CreateItemHandler(uow)
    return await handler.handle(command)


@router.get("", response_model=Paginated[ItemPublic])
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


@router.put("/{item_id}", response_model=ItemPublic)
async def update_item(
    item_id: uuid.UUID,
    item_in: ItemUpdate,
    uow: IUnitOfWork = Depends(get_uow),
    current_user: User = Depends(get_current_active_user),
):
    """
    Update an item owned by the current user.
    Only provided fields will be updated.
    """
    logger.info(
        "--> Entering update_item API endpoint",
        item_id=str(item_id),
        user_id=str(current_user.id),
    )
    logger.debug("Received update data", data=item_in.model_dump())

    command = UpdateItemCommand(
        item_id=item_id, item_in=item_in, owner_id=current_user.id
    )
    handler = UpdateItemHandler(uow)
    try:
        updated_item = await handler.handle(command)
        logger.info(
            "<-- Exiting update_item API endpoint successfully", item_id=str(item_id)
        )
        return updated_item
    except ResourceNotFoundError as e:
        logger.exception("!!! Error in update_item API endpoint", exc_info=e)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.exception("!!! Error in update_item API endpoint", exc_info=e)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(
    item_id: uuid.UUID,
    uow: IUnitOfWork = Depends(get_uow),
    current_user: User = Depends(get_current_active_user),
) -> None:
    """
    Delete an item owned by the current user.
    This performs a soft delete.
    """
    command = DeleteItemCommand(item_id=item_id, owner_id=current_user.id)
    handler = DeleteItemHandler(uow)
    try:
        await handler.handle(command)
    except ResourceNotFoundError as e:
        # For idempotency, you might choose to ignore Not Found errors on DELETE.
        # However, returning a 404 is often clearer for the client.
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    # A 204 response must not have a body, so we return None.
    return None
