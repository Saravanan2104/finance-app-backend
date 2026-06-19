from datetime import date

from sqlalchemy import (
    Column,
    Integer,
    Float,
    String,
    Date,
    Boolean,
    ForeignKey
)

from sqlalchemy.orm import relationship

from models.database import Base


class Loan(Base):
    __tablename__ = "loans"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    customer_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    loan_amount = Column(
        Float,
        nullable=False
    )

    interest_rate = Column(
        Float,
        nullable=False
    )

    balance_amount = Column(
        Float,
        nullable=False
    )

    net_disbursed_amount = Column(
        Float,
        default=0
    )

    emi_amount = Column(
        Float,
        nullable=False
    )

    loan_date = Column(
        Date,
        default=date.today
    )

    last_interest_date = Column(
        Date,
        default=date.today
    )

    status = Column(
        String,
        default="pending"
    )

    approved_by = Column(
        Integer,
        nullable=True
    )

    admin_override = Column(
        Boolean,
        default=False
    )

    customer = relationship(
        "User",
        back_populates="loans"
    )

    payments = relationship(
        "Payment",
        back_populates="loan"
    )