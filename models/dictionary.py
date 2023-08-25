from sqlalchemy import Column, Integer, String, Numeric
from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel
from typing import List, Dict, Optional
from typing import ClassVar, Any
Base = declarative_base()


class Word(Base):
    __tablename__ = "words"
    id = Column(Integer, primary_key=True, index=True)
    word = Column(String(255))
    frequency = Column(Integer)
    avg_freq = Column(Numeric(18, 3))

class ArrayRequest(BaseModel):
    key_list: List[List[Any]]
    pairs: List = None
    chars: List = None

class timeRequest(BaseModel):
    l: List[Dict]

class SentencesModel(BaseModel):
    sentences: List[str]
