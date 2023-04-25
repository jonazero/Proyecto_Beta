from sqlalchemy import Column, Integer, String, Numeric
from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel
from typing import List
Base = declarative_base()


class Word(Base):
    __tablename__ = "words"
    id = Column(Integer, primary_key=True, index=True)
    word = Column(String(255))
    frequency = Column(Integer)
    avg_freq = Column(Numeric(18, 3))


class ArrayRequest(BaseModel):
    letters: List[str]
    limit: int

class SentencesModel(BaseModel):
    sentences: List[str]
