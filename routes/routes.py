from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from starlette.requests import Request
from starlette.templating import Jinja2Templates
from aiortc import RTCPeerConnection, RTCSessionDescription
from src.schemas import Offer
from aiortc.contrib.media import MediaRelay, MediaBlackhole
from camera import ImageProcessing
from models.dictionary import ArrayRequest, SentencesModel
from models.user import UserParamsModel
from jsonwt import get_current_user_params
#from database.db import engine
#from database.dict import query_database
#from models.dictionary import Base
import json
import asyncio
import os
import cv2

routes = APIRouter()
templates = Jinja2Templates(directory="templates")
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_SECRET = os.getenv("GOOGLE_SECRET")
pcs = set()
#Base.metadata.create_all(bind=engine)


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
async def get_words(data: ArrayRequest):
    query_string = "SELECT word FROM words WHERE word LIKE '%"
    letters = data.letters
    limit = data.limit
    for letter in letters:
        query_string += f"{letter}%"
    query_string += f"' LIMIT {limit};"
    rows = query_database(query_string)
    words = [row[0] for row in rows]
    return JSONResponse(content={'words': words})


@routes.post("/sentences/")
async def generate_sentences(sentences: SentencesModel):
    # generateSentences()
    return "hola"


@routes.post("/offer_cv")
async def offer(params: Offer):
    offer = RTCSessionDescription(sdp=params.sdp, type=params.type)
    pc = RTCPeerConnection()
    pcs.add(pc)
    @ pc.on("datachannel")
    def on_datachannel(channel):
        chunks = []
        @ channel.on("message")
        async def on_message(message):
            jsonchunks = json.loads(message)
            chunk = jsonchunks["chunk"]
            totalchunks = jsonchunks["totalchunks"]
            key = jsonchunks["key"]
            if(chunk):
                chunks.append(chunk)
                if(len(chunks) == totalchunks):
                    img_obj = ImageProcessing()
                    img = img_obj.reconstructImage(chunks)
                    cv2.imshow("Image", img)
                    cv2.waitKey(1)
                    results = img_obj.getKeyCoords(img, key)
                    channel.send(json.dumps(results))
                    chunks.clear()


    @ pc.on("connectionstatechange")
    async def on_connectionstatechange():
        print("Connection state is %s" % pc.connectionState)
        if pc.connectionState == "false":
            await pc.close()
            pcs.discard(pc)

    await pc.setRemoteDescription(offer)
    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)
    return {"sdp": pc.localDescription.sdp, "type": pc.localDescription.type}


@ routes.on_event("shutdown")
async def on_shutdown():
    # Close peer connections
    coros = [pc.close() for pc in pcs]
    await asyncio.gather(*coros)
    pcs.clear()

