from fastapi import HTTPException
from sqlalchemy.orm import Session

from models.user import User

from schemas.user import UserUpdate


def get_all_customers(
    db: Session
):
    return db.query(User).filter(
        User.role == "customer"
    ).all()


def get_customer_by_id(
    db: Session,
    customer_id: int
):

    customer = db.query(User).filter(
        User.id == customer_id
    ).first()

    if not customer:
        raise HTTPException(
            status_code=404,
            detail="Customer not found"
        )

    return customer


def update_customer(
    db: Session,
    customer_id: int,
    payload: UserUpdate
):

    customer = db.query(User).filter(
        User.id == customer_id
    ).first()

    if not customer:
        raise HTTPException(
            status_code=404,
            detail="Customer not found"
        )

    customer.name = payload.name
    customer.dob = payload.dob
    customer.phone_no = payload.phone_no
    customer.relative_name = payload.relative_name
    customer.relative_phone = payload.relative_phone
    customer.relative_relation = payload.relative_relation

    db.commit()
    db.refresh(customer)

    return customer


def delete_customer(
    db: Session,
    customer_id: int
):

    customer = db.query(User).filter(
        User.id == customer_id
    ).first()

    if not customer:
        raise HTTPException(
            status_code=404,
            detail="Customer not found"
        )

    db.delete(customer)

    db.commit()

    return {
        "message": "Customer deleted"
    }