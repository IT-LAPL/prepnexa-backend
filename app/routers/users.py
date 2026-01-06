from fastapi import APIRouter, Depends, HTTPException, status

from app.core.security import create_access_token
from app.dependencies.auth import get_current_user
from app.dependencies.services import get_user_service
from app.services.user_service import UserService
from app.models.user import User
from app.schemas.auth import LoginRequest, Token
from app.schemas.user import UserCreate, UserRead

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_new_user(
    user_in: UserCreate,
    user_service: UserService = Depends(get_user_service),
):
    existing = await user_service.get_user_by_email(user_in.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    return await user_service.create_user(user_in)


@router.post("/login", response_model=Token)
async def login(
    data: LoginRequest,
    user_service: UserService = Depends(get_user_service),
):
    user = await user_service.authenticate(data.email, data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    access_token = create_access_token(subject=str(user.id))

    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserRead)
async def profile(
    current_user: User = Depends(get_current_user),
):
    return current_user
