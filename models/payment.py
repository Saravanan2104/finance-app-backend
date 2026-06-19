from datetime import date

from sqlalchemy import (
    Column,
    Integer,
    Float,
    Date,
    ForeignKey
)

from sqlalchemy.orm import relationship

from models.database import Base


class Payment(Base):
    __tablename__ = "payments"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    loan_id = Column(
        Integer,
        ForeignKey("loans.id"),
        nullable=False
    )

    amount = Column(
        Float,
        nullable=False
    )

    payment_date = Column(
        Date,
        default=date.today
    )

    loan = relationship(
        "Loan",
        back_populates="payments"
    )