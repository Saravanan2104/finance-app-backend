from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, Date
from sqlalchemy.orm import relationship
from database import Base
from datetime import date

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    dob = Column(String, nullable=False)
    aadhar = Column(Integer, unique=True, nullable=False)
    pan = Column(String, unique=True, nullable=False)
    phone_no = Column(String, nullable=False)
    relative_name = Column(String)
    relative_phone = Column(String)
    relative_relation = Column(String)
    role = Column(String, default="customer")  # customer / admin
    password = Column(String, nullable=False)

    loans = relationship("Loan", back_populates="customer", foreign_keys="[Loan.customer_id]")
    notifications = relationship("Notification", back_populates="user")

class Loan(Base):
    __tablename__ = "loans"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("users.id"))
    loan_amount = Column(Float)
    interest_rate = Column(Float)
    balance_amount = Column(Float)
    emi_amount = Column(Float)
    loan_date = Column(Date, default=date.today)
    last_interest_date = Column(Date, default=date.today)
    status = Column(String, default="pending")  # pending/active/paid/rejected
    approved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    admin_override = Column(Boolean, default=False)

    customer = relationship("User", back_populates="loans", foreign_keys=[customer_id])

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    message = Column(String, nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(Date, default=date.today)

    user = relationship("User", back_populates="notifications")