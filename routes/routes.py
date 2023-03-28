from fastapi import APIRouter, Body, Depends, HTTPException, status
from fastapi.responses import HTMLResponse
from starlette.requests import Request
from starlette.templating import Jinja2Templates
from aiortc import RTCPeerConnection, RTCSessionDescription
from src.schemas import Offer
from aiortc.contrib.media import MediaRelay, MediaBlackhole
from models.user import User
from database.user import create_user, get_by_id, get_by_email, get_users, delete_user, update_user
from jsonwt import get_current_user_email
from camera import VideoTransformTrack
import json
import asyncio
import os

routes = APIRouter()
templates = Jinja2Templates(directory="templates")
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_SECRET = os.getenv("GOOGLE_SECRET")


@routes.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("inicio.html", {"request": request})


@ routes.get("/signup", response_class=HTMLResponse)
async def signup(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})


@routes.get("/camara")
async def camara(request: Request):
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


# GET USER BY ID


@routes.get("/google/login")
async def google_login(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})


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
