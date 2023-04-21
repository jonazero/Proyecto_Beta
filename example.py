from fastapi import FastAPI
from sqlalchemy import create_engine, Column, Integer, String, DECIMAL
from sqlalchemy.orm import declarative_base, sessionmaker

app = FastAPI()

# Connect to the database
engine = create_engine(
    'mysql+pymysql://admin:*Playa2011aws@database-1.cayjpxvudk3f.us-east-1.rds.amazonaws.com/Diccionario')
Session = sessionmaker(bind=engine)
Base = declarative_base()


class Word(Base):
    __tablename__ = 'words'
    id = Column(Integer, primary_key=True)
    word = Column(String)
    frequency = Column(Integer)


@app.get('/words/{letters}')
async def get_words(letters: str):
    session = Session()
    words = session.query(Word).filter(Word.word.like(f'%{letters}%')).all()
    session.close()
    return {'words': [word.word for word in words]}
