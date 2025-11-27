from pydantic import BaseModel, Field, EmailStr
from enum import Enum


class UserRole(str, Enum):
    admin = "admin"
    teller = "teller"
    customer = "customer"


class CreateUserRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=32)
    pas: str = Field(..., min_length=4, max_length=64)
    vps: str = Field(..., min_length=4, max_length=64)
    role: UserRole
