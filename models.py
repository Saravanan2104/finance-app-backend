from sqlalchemy import Column, Integer, String, Float, Boolean
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, nullable=False)    
    dob = Column(String, nullable=False, nullable=False)
    aadhar = Column(Integer,unique=True, nullable=False)
    pan = Column(Integer, unique=True, nullable=False)
    phone_no = Column(Integer, nullable=False)
    is_customer = Column(Boolean, default=False)

    

class loan_details(Base):
    __tablename__ = "loan details"

    total_loan_amount = Column(Float)  
    balance_amount = Column(Float)
    emi_amount = Column(Float)
    is_paid = Column(Boolean, default=False)
    ROI = Column(Float)








