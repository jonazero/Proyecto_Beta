from pydantic import BaseModel, Field, EmailStr
from uuid import uuid4
from datetime import datetime
from typing import Optional, List


def generate_id():
    return str(uuid4())


def generate_date():
    return str(datetime.now())

class ArrayRequest(BaseModel):
    key: str
    coords: Optional[List[float]]
    time: int

class User(BaseModel):
    id: str = Field(default_factory=generate_id)
    username: str
    email: EmailStr
    pwd: str
    created_at: str = Field(default_factory=generate_date)
    keyData: List[ArrayRequest]



class UserData(BaseModel):
    keyData: List[ArrayRequest]
