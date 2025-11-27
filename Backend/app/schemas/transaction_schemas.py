from pydantic import BaseModel, Field


class TransactionRequest(BaseModel):
    acc_no: str = Field(..., min_length=3, max_length=32)
    pin: str = Field(..., pattern=r"^\d{4}$")
    amount: int = Field(..., gt=0)


class TransferRequest(TransactionRequest):
    rec_acc_no: str = Field(..., min_length=3, max_length=32)
