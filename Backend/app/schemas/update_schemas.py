from pydantic import BaseModel, Field, EmailStr
from .account_schemas import AccountBase


class UpdateMobileRequest(AccountBase):
    omobile: str = Field(..., pattern=r"^\d{10}$")
    nmobile: str = Field(..., pattern=r"^\d{10}$")


class UpdateEmailRequest(AccountBase):
    oemail: EmailStr
    nemail: EmailStr


class ChangePinRequest(AccountBase):
    newpin: str = Field(..., pattern=r"^\d{4}$")
    vnewpin: str = Field(..., pattern=r"^\d{4}$")
