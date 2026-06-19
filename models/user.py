from sqlalchemy import Column, Integer, String
from models.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String, nullable=False)
    dob = Column(String, nullable=False)

    aadhar = Column(String, unique=True, nullable=False)
    pan = Column(String, unique=True, nullable=False)

    phone_no = Column(String, nullable=False)

    relative_name = Column(String)
    relative_phone = Column(String)
    relative_relation = Column(String)

    role = Column(String, default="customer")

    password = Column(String, nullable=False)