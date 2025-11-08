
from pydantic import BaseModel, EmailStr, Field
from enum import Enum

class UserRole(str, Enum):
    admin = "admin"
    teller = "teller"
    customer = "customer"

class AccountBase(BaseModel):
    h: str = Field(..., min_length=3, max_length=32)
    pin: str = Field(..., min_length=4, max_length=4)

class ChangePinRequest(AccountBase):
    newpin: str = Field(..., min_length=4, max_length=4)

class TransactionRequest(AccountBase):
    amount: int = Field(..., gt=0)

class TransferRequest(TransactionRequest):
    r: str = Field(..., min_length=3, max_length=32)

class CreateUserRequest(BaseModel):
    un: str = Field(..., min_length=3, max_length=32)
    pas: str = Field(..., min_length=6, max_length=64)
    vps: str = Field(..., min_length=6, max_length=64)
    role: UserRole

class CreateAccountRequest(BaseModel):
    h: str = Field(..., min_length=1, max_length=64)
    pin: str = Field(..., min_length=4, max_length=4)
    vpin: str = Field(..., min_length=4, max_length=4)
    mobileno: str = Field(..., min_length=10, max_length=10, pattern=r"^\d{10}$")
    gmail: EmailStr

class UpdateMobileRequest(AccountBase):
    nmobile: str = Field(..., min_length=10, max_length=10, pattern=r"^\d{10}$")
    omobile: str = Field(..., min_length=10, max_length=10, pattern=r"^\d{10}$")

class UpdateEmailRequest(AccountBase):
    nemail: EmailStr
    oemail: EmailStr