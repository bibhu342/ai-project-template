# app/schemas/customer.py
from pydantic import BaseModel, EmailStr
from pydantic import ConfigDict


class CustomerCreate(BaseModel):
    name: str
    email: EmailStr


class CustomerUpdateEmail(BaseModel):
    email: EmailStr


class CustomerOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)  # pydantic v2
    id: int
    name: str
    email: EmailStr
