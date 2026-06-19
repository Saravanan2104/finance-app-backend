from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from core.dependencies import get_db

from schemas.auth import (
    LoginRequest,
    TokenResponse
)

from schemas.user import (
    UserCreate,
    UserResponse
)

from services.auth_service import (
    register_user,
    login_user
)

router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)


@router.post(
    "/register",
    response_model=UserResponse
)
def register(
    user: UserCreate,
    db: Session = Depends(get_db)
):
    return register_user(
        db,
        user
    )


@router.post(
    "/login",
    response_model=TokenResponse
)
def login(
    payload: LoginRequest,
    db: Session = Depends(get_db)
):
    return login_user(
        db,
        payload
    )