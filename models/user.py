from pydantic import BaseModel, Field, EmailStr
from uuid import uuid4
from datetime import datetime


def generate_id():
    return str(uuid4())


def generate_date():
    return str(datetime.now())


class User(BaseModel):
    id: str = Field(default_factory=generate_id)
    username: str
    email: EmailStr
    pwd: str
    
    created_at: str = Field(default_factory=generate_date)


class UserParamsModel(BaseModel):
    matriz_errores_promedio: dict
    matriz_tiempo_teclas: dict
    wpm: int
