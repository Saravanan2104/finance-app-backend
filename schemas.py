from pydantic import BaseModel, EmailStr
from datetime import date
from typing import Optional

class UserRegister(BaseModel):
    name: str
    dob: str
    aadhar: int
    pan: str
    phone_no: str
    relative_name: str
    relative_phone: str
    relative_relation: str
    role: str = "customer"
    password: str

class UserLogin(BaseModel):
    aadhar: int
    password: str

class UserResponse(BaseModel):
    id: int
    name: str
    dob: str
    aadhar: int
    pan: str
    phone_no: str
    relative_name: str
    relative_phone: str
    relative_relation: str
    role: str
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class LoanCreate(BaseModel):
    loan_amount: float
    interest_rate: float
    emi_amount: float

class LoanResponse(BaseModel):
    id: int
    customer_id: int
    loan_amount: float
    interest_rate: float
    balance_amount: float
    emi_amount: float
    loan_date: date
    status: str
    admin_override: bool
    class Config:
        from_attributes = True

class NotificationResponse(BaseModel):
    id: int
    user_id: int
    message: str
    is_read: bool
    created_at: date
    class Config:
        from_attributes = True