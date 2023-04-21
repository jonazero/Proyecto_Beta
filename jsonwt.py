import os
from datetime import datetime, timedelta
from jose import jwt, JWTError
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from db import is_token_blacklisted
from database.dict import query_database
from database.user import get_by_email
from starlette.responses import JSONResponse
from models.user import UserParamsModel
from models.dictionary import Word
# Create a fake db:
FAKE_DB = {'jonazeroenigma@gmail.com': {'name': 'Jonathan Israel Diaz Guevara'}}


# Helper to read numbers using var envs
def cast_to_number(id):
    temp = os.environ.get(id)
    if temp is not None:
        try:
            return float(temp)
        except ValueError:
            return None
    return None


# Configuration
API_SECRET_KEY = "jv18SVNLD4FK8d3C7UzG_aSM4ki_vWcBuQJtFUli"
if API_SECRET_KEY is None:
    raise BaseException('Missing API_SECRET_KEY env var.')
API_ALGORITHM = os.environ.get('API_ALGORITHM') or 'HS256'
API_ACCESS_TOKEN_EXPIRE_MINUTES = cast_to_number(
    'API_ACCESS_TOKEN_EXPIRE_MINUTES') or 15
REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 24 * 30

# Token url (We should later create a token url that accepts just a user and a password to use swagger)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/auth/token')

# Error
CREDENTIALS_EXCEPTION = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail='No se pudo verificar al usuario. Intente con otro correo o contraseña',
    headers={'WWW-Authenticate': 'Bearer'},
)


# Create token internal function
def create_access_token(*, data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({'exp': expire})
    encoded_jwt = jwt.encode(to_encode, API_SECRET_KEY,
                             algorithm=API_ALGORITHM)
    return encoded_jwt


def create_refresh_token(email):
    expires = timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)
    return create_access_token(data={'sub': email}, expires_delta=expires)


# Create token for an email
def create_token(email):
    access_token_expires = timedelta(minutes=API_ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={'sub': email}, expires_delta=access_token_expires)
    return access_token


def valid_email_from_db(email):
    return email in FAKE_DB


def decode_token(token):
    return jwt.decode(token, API_SECRET_KEY, algorithms=[API_ALGORITHM])


async def get_current_user_params(token: str = Depends(oauth2_scheme)):
    if is_token_blacklisted(token):
        print("blacklisted token")
        raise CREDENTIALS_EXCEPTION
    try:
        payload = decode_token(token)
        email: str = payload.get('sub')
        if email is None:
            print("email is none")
            raise CREDENTIALS_EXCEPTION
    except JWTError:
        print("credential exception")
        raise CREDENTIALS_EXCEPTION
    params = get_by_email(email)
    if not params:
        raise CREDENTIALS_EXCEPTION
    else:
        return UserParamsModel(**params)


async def get_words_from_dict(token: str = Depends(oauth2_scheme)):
    if is_token_blacklisted(token):
        print("blacklisted token")
        raise CREDENTIALS_EXCEPTION
    try:
        payload = decode_token(token)
        email: str = payload.get('sub')
        if email is None:
            print("email is none")
            raise CREDENTIALS_EXCEPTION
    except JWTError:
        print("credential exception")
        raise CREDENTIALS_EXCEPTION
    query_string = f"SELECT word FROM words WHERE word LIKE '%{letters}%' LIMIT {limit};"
    rows = query_database(query_string)
    words = [row[0] for row in rows]
    return Word(**words)
    
    


async def get_current_user_token(token: str = Depends(oauth2_scheme)):
    _ = await get_current_user_params(token)
    return token
