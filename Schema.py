from pydantic import BaseModel, Field
from typing import Optional, List
from bson import ObjectId
from marshmallow import Schema, fields

class AccountCreate(BaseModel):
    userName: str
    initial_balance: float = Field(default=0.0, ge=0.0)

class AccountDeletionResponseSchema(Schema):
    message = fields.Str(required=True)
    account_id = fields.Str(required=True)

class TransactionRequest(BaseModel):
    amount: float = Field(gt=0.0)
    # We add this field so Pydantic handles it cleanly!
    account_type: str = Field(default="checking")

class TransactionResponse(BaseModel):
    type: str
    amount: float
    timestamp: str

class AccountResponse(BaseModel):
    id: str = Field(alias="_id")
    userName: str
    checking_balance: float = Field(default=0.0)
    savings_balance: float = Field(default=0.0)
    transactions: List[TransactionResponse] = []

    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}