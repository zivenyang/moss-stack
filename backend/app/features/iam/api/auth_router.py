from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from app.features.iam.application.auth.commands.register import RegisterUserCommand, RegisterUserHandler
from app.features.iam.application.auth.commands.login import LoginCommand, LoginHandler
from app.shared.infrastructure.uow import IUnitOfWork
from app.shared.web.deps import get_uow
from ..schemas import Token, UserCreate, UserPublic

router = APIRouter()

@router.post("/login/access-token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    uow: IUnitOfWork = Depends(get_uow)
):
    command = LoginCommand(identifier=form_data.username, password=form_data.password)
    handler = LoginHandler(uow)
    try:
        return await handler.handle(command)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.post("/register", response_model=UserPublic, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_in: UserCreate,
    uow: IUnitOfWork = Depends(get_uow),
):
    """
    Register a new user. The Unit of Work manages the entire transaction.
    """
    command = RegisterUserCommand(user_data=user_in)
    handler = RegisterUserHandler(uow)
    try:
        return await handler.handle(command)
    except Exception as e:
        # Let the global exception middleware handle this.
        raise e