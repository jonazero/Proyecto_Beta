import os
from datetime import datetime
from datetime import timedelta
from authlib.integrations.starlette_client import OAuth
from authlib.integrations.starlette_client import OAuthError
from fastapi import Body, FastAPI, Request, HTTPException, status
from starlette.config import Config
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import JSONResponse
from database.user import create_user, get_by_id, get_by_email, get_users, delete_user, update_user
from typing import Union
from jsonwt import create_refresh_token
from jsonwt import create_token
from jsonwt import CREDENTIALS_EXCEPTION
from jsonwt import decode_token
from jsonwt import valid_email_from_db
from passlib.context import CryptContext
from jose import JWTError, jwt
from models.user import User
# Create the auth app
auth_app = FastAPI()

# OAuth settings
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_SECRET")
if GOOGLE_CLIENT_ID is None or GOOGLE_CLIENT_SECRET is None:
    raise BaseException('Missing env variables')

# Set up OAuth
config_data = {'GOOGLE_CLIENT_ID': GOOGLE_CLIENT_ID,
               'GOOGLE_CLIENT_SECRET': GOOGLE_CLIENT_SECRET}
starlette_config = Config(environ=config_data)
oauth = OAuth(starlette_config)
oauth.register(
    name='google',
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'},
)

# Set up the middleware to read the request session
SECRET_KEY = "jv18SVNLD4FK8d3C7UzG_aSM4ki_vWcBuQJtFUli"
if SECRET_KEY is None:
    raise 'Missing SECRET_KEY'
auth_app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)

# Frontend URL:
FRONTEND_URL = os.getenv('FRONTEND_URL') or "http://localhost:8000/signup"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ACCESS_TOKEN_EXPIRE_MINUTES = 30


def get_user(email: str):
    # Get user from database if exists
    return get_by_email(email)


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)

def authenticate_user(email: str, password: str):
    # Athenticate User:
    user = get_user(email)
    if not user:
        return False
    if not verify_password(password, user[0]['pwd']):
        return False
    return user[0]


def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")
    return encoded_jwt


@auth_app.route('/login')
async def login(request: Request):
    redirect_uri = FRONTEND_URL  # This creates the url for our /auth endpoint
    return await oauth.google.authorize_redirect(request, redirect_uri)


@auth_app.route('/token')
async def auth(request: Request):
    try:
        access_token = await oauth.google.authorize_access_token(request)
    except OAuthError:
        raise CREDENTIALS_EXCEPTION
    user_data = await oauth.google.parse_id_token(request, access_token)
    if get_by_email(user_data["email"]):
        return JSONResponse({
            'result': True,
            'access_token': create_token(user_data['email']),
            'refresh_token': create_refresh_token(user_data['email']),
        })
    raise CREDENTIALS_EXCEPTION


@auth_app.post("/token2")
async def login_for_access_token(email: str = Body(), pwd: str = Body()):
    user = authenticate_user(email, pwd)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user['email']}, expires_delta=access_token_expires
    )
    return {"result": True, "access_token": access_token, "token_type": "bearer"}


# CREATE USER


@auth_app.post("/create-user")
def create(user: User):
    user.pwd =  get_password_hash(user.pwd)
    return (create_user(user.dict()))


@auth_app.post('/refresh')
async def refresh(request: Request):
    try:
        # Only accept post requests
        if request.method == 'POST':
            form = await request.json()
            if form.get('grant_type') == 'refresh_token':
                token = form.get('refresh_token')
                payload = decode_token(token)
                # Check if token is not expired
                if datetime.utcfromtimestamp(payload.get('exp')) > datetime.utcnow():
                    email = payload.get('sub')
                    # Validate email
                    if valid_email_from_db(email):
                        # Create and return token
                        return JSONResponse({'result': True, 'access_token': create_token(email)})

    except Exception:
        raise CREDENTIALS_EXCEPTION
    raise CREDENTIALS_EXCEPTION
