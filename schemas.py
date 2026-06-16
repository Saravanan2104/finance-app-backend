from pydantic import BaseModel

class CustomerCreate(BaseModel):
    name: str
    dob: str
    aadhar: int
    pan: str
    phone_no: str
    relative_name: str
    relative_phone: str
    relative_relation: str

class CustomerResponse(CustomerCreate):
    id: int
    is_customer: bool
    class Config:
        from_attributes = True

class LoanCreate(BaseModel):
    customer_id: int
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
    is_paid: bool
    class Config:
        from_attributes = True