from fastapi import APIRouter, Body
from fastapi.responses import HTMLResponse, RedirectResponse
from starlette.requests import Request
from starlette.templating import Jinja2Templates
from fastapi_sso.sso.google import GoogleSSO
from fastapi_sso.sso.facebook import FacebookSSO
from fastapi_sso.sso.microsoft import MicrosoftSSO
from aiortc import RTCPeerConnection, RTCSessionDescription
from src.schemas import Offer
from aiortc.contrib.media import MediaRelay, MediaBlackhole
from os import getenv
from models.user import User
from database.user import create_user, get_by_id, get_by_email, get_users, delete_user, update_user
from camera import VideoTransformTrack
import json
import asyncio
import os

routes = APIRouter()
templates = Jinja2Templates(directory="templates")
GOOGLE_CLIENT_ID = getenv("GOOGLE_CLIENT_ID")
GOOGLE_SECRET = getenv("GOOGLE_SECRET")
FACEBOOK_CLIENT_ID = getenv("FACEBOOK_CLIENT_ID")
FACEBOOK_SECRET = getenv("FACEBOOK_SECRET")
MICROSOFT_CLIENT_ID = getenv("MICROSOFT_CLIENT_ID")
MICROSOFT_SECRET = getenv("MICROSOFT_SECRET")
MICROSOFT_TENANT = getenv("MICROSOFT_TENANT")

GSSO = GoogleSSO(client_id=GOOGLE_CLIENT_ID, client_secret=GOOGLE_SECRET,
                 allow_insecure_http=True, use_state=False)

FSSO = FacebookSSO(client_id=FACEBOOK_CLIENT_ID, client_secret=FACEBOOK_SECRET,
                   allow_insecure_http=True, use_state=False)

MSSO = MicrosoftSSO(client_id=MICROSOFT_CLIENT_ID, client_secret=MICROSOFT_SECRET,
                    tenant=MICROSOFT_TENANT, allow_insecure_http=True, use_state=False)

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"


@routes.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("inicio.html", {"request": request})


@routes.get("/google/login/auth")
async def google_login_auth(request: Request):
    """Initialize auth and redirect"""
    return await GSSO.get_login_redirect(redirect_uri=request.url_for("google_login"), params={"prompt": "consent", "access_type": "offline"})



@routes.get("/google/signup/auth")
async def google_signing_auth(request: Request):
    """Initialize auth and redirect"""
    return await GSSO.get_login_redirect(redirect_uri=request.url_for("google_signup"), params={"prompt": "consent", "access_type": "offline"})


@routes.get("/facebook/login/auth")
async def facebook_login_auth(request: Request):
    return await FSSO.get_login_redirect(redirect_uri=request.url_for("facebook_login"), params={"prompt": "consent", "access_type": "offline"})


@routes.get("/microsoft/login/auth")
async def microsoft_login_auth(request: Request):
    return await MSSO.get_login_redirect(redirect_uri=request.url_for("microsoft_login"), params={"prompt": "consent", "access_type": "offline"})


@ routes.get("/signup", response_class=HTMLResponse)
async def camara(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})


@routes.get("/camara")
async def camara(request: Request):
    # user = await GSSO.verify_and_process(request)
    # print(user)
    return templates.TemplateResponse("index.html", {"request": request})


@routes.post("/offer_cv")
async def offer(params: Offer):
    offer = RTCSessionDescription(sdp=params.sdp, type=params.type)
    pc = RTCPeerConnection()
    pcs.add(pc)
    recorder = MediaBlackhole()
    relay = MediaRelay()
    stream = None
    esc = False

    @ pc.on("datachannel")
    def on_datachannel(channel):
        @ channel.on("message")
        async def on_message(message):
            nonlocal esc
            if esc == False:
                if message == "Escape":
                    esc = True
                    stream.transform = True
                r = await stream.set_keys(message)
                if r != None:
                    channel.send(json.dumps(r))
            else:
                reci = await stream.test_keys(message)
                if reci["error"] == False:
                    channel.send(json.dumps(reci))

    @ pc.on("connectionstatechange")
    async def on_connectionstatechange():
        print("Connection state is %s" % pc.connectionState)
        if pc.connectionState == "false":
            await pc.close()
            pcs.discard(pc)

    @ pc.on("track")
    def on_track(track):
        nonlocal stream
        if track.kind == "video":
            stream = VideoTransformTrack(relay.subscribe(
                track), transform=params.video_transform)
            pc.addTrack(stream)

        @ track.on("ended")
        async def on_ended():
            await recorder.stop()
    await pc.setRemoteDescription(offer)
    await recorder.start()

    answer = await pc.createAnswer()
    await pc.setRemoteDescription(offer)
    await pc.setLocalDescription(answer)
    return {"sdp": pc.localDescription.sdp, "type": pc.localDescription.type}
pcs = set()
args = ''


@ routes.on_event("shutdown")
async def on_shutdown():
    # Close peer connections
    coros = [pc.close() for pc in pcs]
    await asyncio.gather(*coros)
    pcs.clear()

# CREATE USER


@routes.post("/create-user", response_model=User)
def create(user: User):
    return (create_user(user.dict()))


# GET USER BY ID


@routes.get("/google/login")
async def google_login(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})


@routes.get("/get-access-token")
async def getAccessToken(request: Request):
    content = await GSSO.verify_and_process(request)
    return content


@routes.get("/google/signup")
async def google_signup(request: Request):
    usuario = await GSSO.verify_and_process(request)
    return usuario


@routes.get("facebook/login")
async def facebook_login(request: Request):
    user = await FSSO.verify_and_process(request)
    return user


@routes.get("microsoft/login")
async def microsoft_login(request: Request):
    user = await MSSO.verify_and_process(request)
    return user


@routes.get("/get-user-id/{id}")
async def getuser(id: str):
    return get_by_id(id)


@routes.post("/get-user-email")
async def getUserEmail(email: str = Body()):
    return get_by_email(email)

# GET ALL USERS


@routes.get("/all")
def get_all():
    return get_users()


# DELETE USER


@routes.post("/delete")
def create(user: User):
    return delete_user(user.dict())

# UPDATE USER


@routes.post("/update")
def create(user: User):
    return update_user(user.dict())