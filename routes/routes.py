from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from starlette.requests import Request
from starlette.templating import Jinja2Templates
from fastapi_sso.sso.google import GoogleSSO
from fastapi.staticfiles import StaticFiles
from aiortc import RTCPeerConnection, RTCSessionDescription
from src.schemas import Offer
from aiortc.contrib.media import MediaRelay, MediaBlackhole
from os import getenv
from camera import VideoTransformTrack
import json
import asyncio
import os
routes = APIRouter()
routes.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")
GOOGLE_CLIENT_ID = getenv("GOOGLE_CLIENT_ID")
GOOGLE_SECRET = getenv("GOOGLE_SECRET")
SSO = GoogleSSO(client_id=GOOGLE_CLIENT_ID, client_secret=GOOGLE_SECRET,
                redirect_uri="http://localhost:8000/camara", allow_insecure_http=True, use_state=False)

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"


@routes.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("inicio.html", {"request": request})


@routes.get("/auth/login")
async def auth_init():
    """Initialize auth and redirect"""
    return await SSO.get_login_redirect(params={"prompt": "consent", "access_type": "offline"})


@ routes.get("/signup", response_class=HTMLResponse)
async def camara(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})


@routes.get("/camara")
async def camara(request: Request):
    user = await SSO.verify_and_process(request)
    print(user)
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
