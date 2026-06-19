from datetime import date

from fastapi import HTTPException
from sqlalchemy.orm import Session

from models.loan import Loan
from models.user import User
from models.payment import Payment
from models.notification import Notification

from schemas.loan import LoanCreate


def add_notification(
    db: Session,
    user_id: int,
    message: str
):

    notification = Notification(
        user_id=user_id,
        message=message
    )

    db.add(notification)
    db.commit()


def apply_loan(
    db: Session,
    current_user,
    payload: LoanCreate
):

    if current_user.role != "customer":
        raise HTTPException(
            status_code=403,
            detail="Only customers can apply for loans"
        )

    pending_loan = db.query(Loan).filter(
        Loan.customer_id == current_user.id,
        Loan.status == "pending"
    ).first()

    if pending_loan:
        raise HTTPException(
            status_code=400,
            detail="Pending loan already exists"
        )

    active_loan = db.query(Loan).filter(
        Loan.customer_id == current_user.id,
        Loan.status == "active"
    ).first()

    old_balance = (
        active_loan.balance_amount
        if active_loan
        else 0
    )

    interest_amount = (
        payload.loan_amount *
        payload.interest_rate
    ) / 100

    net_amount = (
        payload.loan_amount
        - interest_amount
        - old_balance
    )

    if net_amount <= 0:
        raise HTTPException(
            status_code=400,
            detail="Not eligible for loan"
        )

    loan = Loan(
        customer_id=current_user.id,
        loan_amount=payload.loan_amount,
        interest_rate=payload.interest_rate,
        balance_amount=payload.loan_amount,
        net_disbursed_amount=net_amount,
        emi_amount=payload.emi_amount,
        loan_date=date.today(),
        last_interest_date=date.today(),
        status="pending"
    )

    db.add(loan)
    db.commit()
    db.refresh(loan)

    admins = db.query(User).filter(
        User.role == "admin"
    ).all()

    for admin in admins:
        add_notification(
            db,
            admin.id,
            f"New loan application from {current_user.name}"
        )

    return loan


def get_all_loans(
    db: Session
):
    return db.query(Loan).all()


def get_my_loans(
    db: Session,
    current_user
):
    return db.query(Loan).filter(
        Loan.customer_id == current_user.id
    ).all()


def get_pending_loans(
    db: Session
):
    return db.query(Loan).filter(
        Loan.status == "pending"
    ).all()


def approve_loan(
    db: Session,
    loan_id: int,
    admin,
    override: bool = False
):

    loan = db.query(Loan).filter(
        Loan.id == loan_id
    ).first()

    if not loan:
        raise HTTPException(
            status_code=404,
            detail="Loan not found"
        )

    if loan.status != "pending":
        raise HTTPException(
            status_code=400,
            detail="Loan is not pending"
        )

    active_loan = db.query(Loan).filter(
        Loan.customer_id == loan.customer_id,
        Loan.status == "active"
    ).first()

    if active_loan:
        active_loan.status = "closed"

    loan.status = "active"
    loan.approved_by = admin.id
    loan.admin_override = override

    db.commit()
    db.refresh(loan)

    add_notification(
        db,
        loan.customer_id,
        f"Loan approved. Amount credited: {loan.net_disbursed_amount}"
    )

    return loan


def reject_loan(
    db: Session,
    loan_id: int
):

    loan = db.query(Loan).filter(
        Loan.id == loan_id
    ).first()

    if not loan:
        raise HTTPException(
            status_code=404,
            detail="Loan not found"
        )

    loan.status = "rejected"

    db.commit()
    db.refresh(loan)

    add_notification(
        db,
        loan.customer_id,
        f"Loan of {loan.loan_amount} rejected"
    )

    return loan


def pay_emi(
    db: Session,
    loan_id: int,
    amount: float,
    current_user
):

    loan = db.query(Loan).filter(
        Loan.id == loan_id,
        Loan.customer_id == current_user.id
    ).first()

    if not loan:
        raise HTTPException(
            status_code=404,
            detail="Loan not found"
        )

    if loan.status != "active":
        raise HTTPException(
            status_code=400,
            detail="Loan is not active"
        )

    payment = Payment(
        loan_id=loan.id,
        amount=amount
    )

    db.add(payment)

    loan.balance_amount -= amount

    if loan.balance_amount <= 0:
        loan.balance_amount = 0
        loan.status = "paid"

        add_notification(
            db,
            current_user.id,
            "Loan fully paid"
        )

    db.commit()
    db.refresh(loan)

    return loan


def recalculate_interest(
    db: Session,
    loan_id: int
):

    loan = db.query(Loan).filter(
        Loan.id == loan_id
    ).first()

    if not loan:
        raise HTTPException(
            status_code=404,
            detail="Loan not found"
        )

    if loan.status != "active":
        raise HTTPException(
            status_code=400,
            detail="Loan is not active"
        )

    days_since = (
        date.today()
        - loan.last_interest_date
    ).days

    if days_since >= 30:

        interest = (
            loan.balance_amount
            * loan.interest_rate
        ) / 100

        loan.balance_amount += interest

        loan.last_interest_date = date.today()

        db.commit()
        db.refresh(loan)

        add_notification(
            db,
            loan.customer_id,
            f"Interest added: {interest}"
        )

    return loan