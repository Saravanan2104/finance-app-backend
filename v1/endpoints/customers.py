from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from core.dependencies import get_db

from schemas.user import (
    UserUpdate,
    UserResponse
)

from services.customer_service import (
    get_all_customers,
    get_customer_by_id,
    update_customer,
    delete_customer
)

router = APIRouter(
    prefix="/customers",
    tags=["Customers"]
)


@router.get(
    "/",
    response_model=list[UserResponse]
)
def get_customers(
    db: Session = Depends(get_db)
):
    return get_all_customers(db)


@router.get(
    "/{customer_id}",
    response_model=UserResponse
)
def get_customer(
    customer_id: int,
    db: Session = Depends(get_db)
):
    return get_customer_by_id(
        db,
        customer_id
    )


@router.put(
    "/{customer_id}",
    response_model=UserResponse
)
def update_customer_data(
    customer_id: int,
    payload: UserUpdate,
    db: Session = Depends(get_db)
):
    return update_customer(
        db,
        customer_id,
        payload
    )


@router.delete(
    "/{customer_id}"
)
def delete_customer_data(
    customer_id: int,
    db: Session = Depends(get_db)
):
    return delete_customer(
        db,
        customer_id
    )