from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

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
    is_customer = Column(Boolean, default=False)

    loans = relationship("Loan", back_populates="customer")

class Loan(Base):
    __tablename__ = "loans"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("users.id"))
    loan_amount = Column(Float)
    interest_rate = Column(Float)
    balance_amount = Column(Float)
    emi_amount = Column(Float)
    is_paid = Column(Boolean, default=False)
    alert_sent = Column(Boolean, default=False)

    customer = relationship("User", back_populates="loans")