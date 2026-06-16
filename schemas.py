from pydantic import BaseModel

class Relative(BaseModel):
    name: str
    phone_no: int
    relation: str

class Customer(BaseModel):    
    name : str
    aadhar_no: str
    pan_no: str
    DOB: str
    phone_no: str

class Apply_loan(BaseModel):
    user_details: Customer
    relative_details: Relative
    loan_amount: float
    interest: float
