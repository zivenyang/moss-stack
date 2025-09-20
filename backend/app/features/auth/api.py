from fastapi import APIRouter, Depends, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
from app.shared.infrastructure.db.session import get_db_session
from .domain.user import UserCreate, UserPublic
from .schemas import LoginRequest, Token
from .commands.register_user import RegisterUserCommand, RegisterUserHandler
from .commands.login_user import LoginUserCommand, LoginUserHandler

router = APIRouter()

@router.post("/users/register", response_model=UserPublic, status_code=201)
async def register_user(
    user_in: UserCreate,
    session: AsyncSession = Depends(get_db_session)
):
    """
    Register a new user.
    """
    command = RegisterUserCommand(user_data=user_in)
    handler = RegisterUserHandler(session)
    result = await handler.handle(command)
    
    if not result.is_success:
        # BusinessRuleViolationError translates to 400 Bad Request
        raise HTTPException(status_code=400, detail=result.error.message)
    
    return result.get_value()

@router.post("/login/access-token", response_model=Token)
async def login_for_access_token(
    login_data: LoginRequest,
    session: AsyncSession = Depends(get_db_session)
):
    """
    OAuth2 compatible token login, get an access token for future requests.
    """
    command = LoginUserCommand(login_data=login_data)
    handler = LoginUserHandler(session)
    result = await handler.handle(command)

    if not result.is_success:
        # AuthorizationError translates to 401 Unauthorized
        raise HTTPException(status_code=401, detail=result.error.message)

    return result.get_value()