from fastapi import FastAPI
from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse
from starlette.requests import Request
from starlette.templating import Jinja2Templates
from aiortc import RTCPeerConnection, RTCSessionDescription
from src.schemas import Offer
from aiortc.contrib.media import MediaRelay, MediaBlackhole
from camera import VideoTransformTrack
from models.user import UserParamsModel
from jsonwt import get_current_user_params
from sqlalchemy.orm import Session
from sqlalchemy import text
from database.db import SessionLocal, engine
from database.dict import query_database
from models.dictionary import Word, Base
from pydantic import BaseModel
from typing import List
import json
import asyncio
import os

routes = APIRouter()
templates = Jinja2Templates(directory="templates")
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_SECRET = os.getenv("GOOGLE_SECRET")
pcs = set()
Base.metadata.create_all(bind=engine)


@routes.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("inicio.html", {"request": request})


@ routes.get("/signup", response_class=HTMLResponse)
async def signup(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})


@routes.get("/camara")
async def camara(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@routes.get("/user/params")
async def UserParams(params: UserParamsModel = Depends(get_current_user_params)):
    return params


@routes.post("/words/")
async def get_words(letters: List[str], limit: int = 10):
    query_string = "SELECT word FROM words WHERE word LIKE '%"
    for letter in letters:
        query_string += f"{letter}%"
    query_string += f"' LIMIT {limit};"
    rows = query_database(query_string)
    words = [row[0] for row in rows]
    return {'words': words}

@routes.post("/offer_cv")
async def offer(params: Offer):
    offer = RTCSessionDescription(sdp=params.sdp, type=params.type)
    pc = RTCPeerConnection()
    pcs.add(pc)
    recorder = MediaBlackhole()
    relay = MediaRelay()
    stream = None

    @ pc.on("datachannel")
    def on_datachannel(channel):
        @ channel.on("message")
        async def on_message(message):
            msg = json.loads(message)
            key = msg["key"]
            print(msg)
            status = msg["status"]
            if status == 0 or status == 1:
                channel.send(json.dumps(await stream.set_keys(key, status)))
            else:
                print("caca")

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


@ routes.on_event("shutdown")
async def on_shutdown():
    # Close peer connections
    coros = [pc.close() for pc in pcs]
    await asyncio.gather(*coros)
    pcs.clear()
