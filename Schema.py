from pydantic import BaseModel, Field
from typing import Optional, List
from bson import ObjectId

class AccountCreate(BaseModel):
    userName: str
    initial_balance: float = Field(default=0.0, ge=0.0) # ge=0.0 forces positive numbers

class TransactionRequest(BaseModel):
    amount: float = Field(gt=0.0) # gt=0.0 forces deposits/withdrawals to be greater than 0

class TransactionResponse(BaseModel):
    type: str # "deposit" or "withdrawal"
    amount: float
    timestamp: str

class AccountResponse(BaseModel):
    id: str = Field(alias="_id")
    userName: str
    balance: float
    transactions: List[TransactionResponse] = []

    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}