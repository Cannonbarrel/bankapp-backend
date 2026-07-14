from pydantic import BaseModel, Field
from typing import Optional
from bson import ObjectId

class ItemCreate(BaseModel):
    name: str
    description: Optional[str] = None
    Swaglevel: float

class ItemUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    Swaglevel: Optional[float] = None

class ItemResponse(BaseModel):
    id: str = Field(alias="_id")
    name: str
    description: Optional[str] = None
    Swaglevel: float

    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}
        json_encoders = {ObjectId: str}