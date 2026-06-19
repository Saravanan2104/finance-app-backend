from fastapi import HTTPException
from sqlalchemy.orm import Session

from models.user import User

from schemas.user import UserCreate
from schemas.auth import LoginRequest

from core.security import (
    hash_password,
    verify_password,
    create_access_token
)


def register_user(
    db: Session,
    user: UserCreate
):

    existing_user = db.query(User).filter(
        (User.aadhar == user.aadhar)
        | (User.pan == user.pan)
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Aadhar or PAN already registered"
        )

    new_user = User(
        name=user.name,
        dob=user.dob,
        aadhar=user.aadhar,
        pan=user.pan,
        phone_no=user.phone_no,
        relative_name=user.relative_name,
        relative_phone=user.relative_phone,
        relative_relation=user.relative_relation,
        role=user.role,
        password=hash_password(user.password)
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


def login_user(
    db: Session,
    payload: LoginRequest
):

    user = db.query(User).filter(
        User.aadhar == payload.aadhar
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    if not verify_password(
        payload.password,
        user.password
    ):
        raise HTTPException(
            status_code=401,
            detail="Incorrect password"
        )

    token = create_access_token(
        {
            "sub": str(user.aadhar)
        }
    )

    return {
        "access_token": token,
        "token_type": "bearer"
    }