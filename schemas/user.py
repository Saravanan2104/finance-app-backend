from pydantic import BaseModel, ConfigDict


class UserCreate(BaseModel):
    name: str
    dob: str
    aadhar: str
    pan: str
    phone_no: str
    relative_name: str
    relative_phone: str
    relative_relation: str
    role: str = "customer"
    password: str


class UserUpdate(BaseModel):
    name: str
    dob: str
    phone_no: str
    relative_name: str
    relative_phone: str
    relative_relation: str


class UserResponse(BaseModel):
    id: int
    name: str
    dob: str
    aadhar: str
    pan: str
    phone_no: str
    relative_name: str
    relative_phone: str
    relative_relation: str
    role: str

    model_config = ConfigDict(
        from_attributes=True
    )