from fastapi import APIRouter
from models.user import User
from database.user import create_user, get_by_id, get_by_email, get_users, delete_user, update_user
from starlette.requests import Request
from fastapi_sso.sso.google import GoogleSSO
from os import getenv
routes_user = APIRouter()

GOOGLE_CLIENT_ID = getenv("GOOGLE_CLIENT_ID")
GOOGLE_SECRET = getenv("GOOGLE_SECRET")
SSO = GoogleSSO(client_id=GOOGLE_CLIENT_ID, client_secret=GOOGLE_SECRET,
                redirect_uri="http://localhost:8000/user/get/{id}", allow_insecure_http=True, use_state=False)
# CREATE USER


@routes_user.post("/create", response_model=User)
def create(user: User):
    return create_user(user.dict())

# GET USER BY ID


@routes_user.get("/login/{id}")
async def get_by_id(request: Request):
    user = await SSO.verify_and_process(request)
    try:
        return get_by_id(user.id)
    except:
        return "No hubo"



# GET ALL USERS


@routes_user.get("/all")
def get_all():
    return get_users()

# DELETE USER


@routes_user.post("/delete")
def create(user: User):
    return delete_user(user.dict())

# UPDATE USER


@routes_user.post("/update")
def create(user: User):
    return update_user(user.dict())
