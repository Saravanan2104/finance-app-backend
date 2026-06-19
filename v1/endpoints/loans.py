from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from core.auth import get_current_user, require_admin

from core.dependencies import get_db

from schemas.loan import (
    LoanCreate,
    LoanResponse
)

from services.loan_service import (
    apply_loan,
    get_all_loans,
    get_my_loans,
    get_pending_loans,
    approve_loan,
    reject_loan,
    pay_emi,
    recalculate_interest
)

router = APIRouter(
    prefix="/loans",
    tags=["Loans"]
)


@router.post(
    "/apply",
    response_model=LoanResponse
)
def create_loan(
    payload: LoanCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return apply_loan(
        db=db,
        current_user=current_user,
        payload=payload
    )


@router.get(
    "/",
    response_model=list[LoanResponse]
)
def get_loans(
    db: Session = Depends(get_db)
):
    return get_all_loans(db)


@router.get(
    "/my",
    response_model=list[LoanResponse]
)
def my_loans(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return get_my_loans(
        db,
        current_user
    )


@router.get(
    "/pending",
    response_model=list[LoanResponse]
)
def pending_loans(
    db: Session = Depends(get_db)
):
    return get_pending_loans(db)


@router.put(
    "/{loan_id}/approve",
    response_model=LoanResponse
)
def approve_customer_loan(
    loan_id: int,
    override: bool = False,
    db: Session = Depends(get_db),
    admin=Depends(require_admin)
):
    return approve_loan(
        db=db,
        loan_id=loan_id,
        admin=admin,
        override=override
    )


@router.put(
    "/{loan_id}/reject",
    response_model=LoanResponse
)
def reject_customer_loan(
    loan_id: int,
    db: Session = Depends(get_db),
    admin=Depends(require_admin)
):
    return reject_loan(
        db=db,
        loan_id=loan_id
    )


@router.put(
    "/{loan_id}/pay",
    response_model=LoanResponse
)
def pay_loan_emi(
    loan_id: int,
    amount: float = Query(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return pay_emi(
        db=db,
        loan_id=loan_id,
        amount=amount,
        current_user=current_user
    )


@router.put(
    "/{loan_id}/recalculate",
    response_model=LoanResponse
)
def recalculate_loan_interest(
    loan_id: int,
    db: Session = Depends(get_db),
    admin=Depends(require_admin)
):
    return recalculate_interest(
        db=db,
        loan_id=loan_id
    )