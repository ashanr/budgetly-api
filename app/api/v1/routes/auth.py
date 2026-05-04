from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.repositories.user_repository import UserRepository
from app.schemas.user import LoginRequest, UserCreate, TokenResponse, UserResponse, RefreshRequest
from app.schemas.common import APIResponse
from app.core.security import verify_password, create_access_token, create_refresh_token, decode_token, get_current_user_id

router = APIRouter(prefix="/auth")


@router.post("/login", response_model=APIResponse)
async def login(payload: LoginRequest, db: AsyncSession = Depends(get_db)):
    repo = UserRepository(db)
    user = await repo.get_by_email(payload.email)
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is inactive")

    access_token = create_access_token({"sub": user.id})
    refresh_token = create_refresh_token({"sub": user.id})

    return APIResponse.ok(
        data=TokenResponse(access_token=access_token, refresh_token=refresh_token).model_dump(),
        message="Login successful",
    )


@router.post("/register", response_model=APIResponse)
async def register(payload: UserCreate, db: AsyncSession = Depends(get_db)):
    repo = UserRepository(db)
    existing = await repo.get_by_email(payload.email)
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")
    existing_username = await repo.get_by_username(payload.username)
    if existing_username:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already taken")

    user = await repo.create(
        email=payload.email,
        username=payload.username,
        password=payload.password,
        full_name=payload.full_name,
        currency=payload.currency,
        timezone=payload.timezone,
    )

    access_token = create_access_token({"sub": user.id})
    refresh_token = create_refresh_token({"sub": user.id})

    return APIResponse.ok(
        data={
            "user": UserResponse.model_validate(user).model_dump(),
            "tokens": TokenResponse(access_token=access_token, refresh_token=refresh_token).model_dump(),
        },
        message="Registration successful",
    )


@router.post("/refresh", response_model=APIResponse)
async def refresh_token(payload: RefreshRequest):
    payload_data = decode_token(payload.refresh_token)
    if payload_data.get("type") != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
    user_id = payload_data.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    access_token = create_access_token({"sub": user_id})
    refresh_token_new = create_refresh_token({"sub": user_id})

    return APIResponse.ok(
        data=TokenResponse(access_token=access_token, refresh_token=refresh_token_new).model_dump(),
        message="Token refreshed",
    )


@router.post("/logout", response_model=APIResponse)
async def logout(user_id: str = Depends(get_current_user_id)):
    return APIResponse.ok(message="Logged out successfully")


@router.get("/me", response_model=APIResponse)
async def me(user_id: str = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    repo = UserRepository(db)
    user = await repo.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return APIResponse.ok(data=UserResponse.model_validate(user).model_dump(), message="User retrieved")
