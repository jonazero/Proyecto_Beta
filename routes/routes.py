from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from starlette.requests import Request
from starlette.templating import Jinja2Templates
from aiortc import RTCPeerConnection, RTCSessionDescription
from src.schemas import Offer
from knn import KNN
from camera import ImageProcessing
from models.dictionary import ArrayRequest, SentencesModel
from models.user import UserParamsModel
from jsonwt import get_current_user_params
# from database.db import engine
# from database.dict import query_database
# from models.dictionary import Base
import json
import asyncio
import os
import asyncio
routes = APIRouter()
templates = Jinja2Templates(directory="templates")
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_SECRET = os.getenv("GOOGLE_SECRET")
pcs = set()
# Base.metadata.create_all(bind=engine)


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
    # rows = query_database(query_string)
    # words = [row[0] for row in rows]
    # return JSONResponse(content={'words': words})


@routes.post("/offer_cv")
async def offer(params: Offer):
    offer = RTCSessionDescription(sdp=params.sdp, type=params.type)
    pc = RTCPeerConnection()
    pcs.add(pc)

    @ pc.on("datachannel")
    def on_datachannel(channel):
        chunks = []
        kd = set()
        img_obj = ImageProcessing()
        knn_obj = KNN()
        @ channel.on("message")
        async def on_message(message):
            nonlocal kd
            jsonchunks = json.loads(message)
            if ("flag" in jsonchunks):
                if (jsonchunks["flag"] == 1):
                    benchmark_keys =  jsonchunks["benchmark_keys"]
                    camera_keys = jsonchunks["camera_keys"]
                    practice_char = []
                    X_train = []
                    y_train = []
                    X_test = []
                    for label, samples in camera_keys.items():
                        coords = [sample['coordenadas'] for sample in samples]
                        X_train.extend(coords)
                        y_train.extend([label] * len(coords))
                    for _, samples in benchmark_keys.items():
                        coords = [sample['coordenadas'] for sample in samples]
                        X_test.extend(coords)
                    knn_obj.fit(X_train, y_train)
                    y_pred = knn_obj.predict(X_test)
                    valueslist = list(benchmark_keys.values())
                    keyslist = list(camera_keys.keys())
                    for i, value in enumerate(keyslist):
                        if (value == y_pred[i]):
                            camera_keys[keyslist[i]].append(valueslist[i])
                        else:
                            practice_char.append(value)
                    channel.send(json.dumps({"flag": 1, "keys": practice_char}))
                    return
                    """
                    for label, samples in keysecond.items():
                        X_train.extend(samples)
                        y_train.extend([label] * len(samples))
                    for _, samples in keysfirst.items():
                        X_test.extend(samples)
                    knn_obj.fit(X_train, y_train)
                    y_pred = knn_obj.predict(X_test)
                    kfkeys = list(keysfirst.keys())
                    kfvalues = list(keysfirst.values())
                    for i, value in enumerate(kfkeys):
                        if (value == y_pred[i]):
                            print(value, y_pred[i])
                            keysecond[kfkeys[i]].append(kfvalues[i])
                        else:
                            practice_char.append(value)
                    print(practice_char)
                    channel.send(json.dumps({"msg": 1, "keys": practice_char}))
                    return 
                else:
                    X_train  = []
                    y_train = []
                    for label, samples in keysecond.items():
                        X_train.extend(samples)
                        y_train.extend([label] * len(samples))
                    knn_obj.fit(X_train, y_train)
                    return
                    """


            key = jsonchunks["key"]
            chunk = jsonchunks["chunk"]
            totalchunks = jsonchunks["totalchunks"]
            idx = jsonchunks["index"]
            time = jsonchunks["time"]
            status = jsonchunks["status"]
            kd.add(idx)
            if (chunk):
                chunks.append(chunk)
                if (len(chunks) == totalchunks and len(kd) != 0):
                    img = img_obj.reconstructImage(chunks)
                    # +cv2.imshow("Image", img)
                    # cv2.waitKey(1)
                    results = img_obj.getKeyCoords(img, key, time)
                    if results is None:
                        results = {}
                        results["error"] = "Error: tecla presionada con el dedo incorrecto"
                    elif ("error" in results):
                        kd.clear()
                    elif status == 2:
                        test = results["coords"]
                        pred = knn_obj.predict([test])
                        print(key, pred)
                        if pred[0] != key:
                            results["error"] = "Error: tecla presionada con el dedo incorrecto"
                    jsonresults = json.dumps(results)
                    channel.send(jsonresults)
                    chunks.clear()
                    kd.clear()


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
