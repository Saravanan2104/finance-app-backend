from datetime import date

from pydantic import BaseModel, ConfigDict


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

    net_disbursed_amount: float

    emi_amount: float

    loan_date: date

    status: str

    admin_override: bool

    model_config = ConfigDict(
        from_attributes=True
    )