from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from starlette.requests import Request
from starlette.templating import Jinja2Templates
from aiortc import RTCPeerConnection, RTCSessionDescription
from src.schemas import Offer
from knn import KNN
from textgen import generateSentences
from camera import ImageProcessing
from models.dictionary import ArrayRequest, SentencesModel
from models.user import UserParamsModel
from jsonwt import get_current_user_params
from database.db import engine
from database.user import update_user
from database.dict import query_database
from models.dictionary import Base
from helpers import generate_chars_probability,list2Tuples, lists2TimeTuples, generate_sequences_probability
from collections import Counter
import json
import asyncio
import os
import asyncio
import random
from typing import List
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


async def query_db_words(queryword, limit):
    query_string = "SELECT word FROM words WHERE word LIKE '%"
    query_string += queryword
    query_string += f"' LIMIT {100}"
    query_string = f"SELECT word FROM ({query_string}) AS subconsulta ORDER BY RAND () LIMIT {limit};"
    result = query_database(query_string)
    if result:
        return result[0][0]

@routes.post("/words/")
async def words(data: List[ArrayRequest]):
    starting_text = ["El", "La", "Mi", "Ella",
                     "Había", "Una", "Su", "Sus", "Ellos", "Las", "Los", "De"]
    dataError = []
    dataTimeError = []

    for i, d in enumerate(data):
        if d.key.isalnum():
            dataError.append({"key": d.key, 'coords': d.coords, 'time': d.time})
            if len(data) - i > 1 and d.coords != None:
                if data[i + 1].key.isalnum() and data[i+1].coords != None:
                    dataTimeError.append({"key": d.key, 'coords': d.coords, 'time': d.time})
                    dataTimeError.append({"key": data[i+1].key, 'coords': data[i+1].coords, 'time': data[i+1].time})

    random.shuffle(starting_text)
    charTuples = list2Tuples(dataError)   
    timeTuples = lists2TimeTuples(dataTimeError)
    chars= generate_chars_probability(charTuples, 5)
    pairs = generate_sequences_probability(timeTuples, 5)
    practice_words = []
    if (chars is not None):
        for char_error in chars:
            response = await query_db_words(f"{char_error}%", 1)
            practice_words.append(response)

    if (pairs is not None):
        frecuencia = {}
        for par in pairs:
            if par in frecuencia:
                frecuencia[par] += 1
            else:
                frecuencia[par] = 1
        pairs = [par + (count,) for par, count in frecuencia.items()]
        for tupleerror in pairs:
            response = await query_db_words(f"{tupleerror[0]+tupleerror[1]}%", tupleerror[2])
            if response is not None:
                practice_words.append(response)
    try:
        oraciones = generateSentences(practice_words, starting_text)
        oraciones_minusculas = [palabra.lower() for palabra in oraciones]
        return JSONResponse(content={'oraciones': oraciones_minusculas})
    except:
        for i, palabra in practice_words:
            palabra[i] = palabra[i].lower()
        return JSONResponse(content={'oraciones': practice_words})

    '''
    seqt_tuples = lists2TimeTuples(key_list)
    char_errors = generate_chars_probability(char_tuples, 5)
    seq_errors = generate_sequences_probability(seqt_tuples, 5)
    practice_words = []
    if (char_errors is not None):
        for char_error in char_errors:
            practice_words.append(await query_db_words(f"{char_error}%"))
    if (seq_errors is not None):
        for tupleerror in seq_errors:
            response = await query_db_words(f"{tupleerror[0]+tupleerror[1]}%")
            if response is not None:
                practice_words.append(response)
    try:
        oraciones = generateSentences(practice_words, starting_text)
        oraciones_minusculas = [palabra.lower() for palabra in oraciones]
        return JSONResponse(content={'oraciones': oraciones_minusculas})
    except:
        for i, palabra in practice_words:
            palabra[i] = palabra[i].lower()
        return JSONResponse(content={'oraciones': practice_words})
    # Implementar if para no consultar la base de datos
    '''


@routes.post("/offer_cv")
async def offer(params: Offer):
    offer = RTCSessionDescription(sdp=params.sdp, type=params.type)
    pc = RTCPeerConnection()
    pcs.add(pc)

    @ pc.on("datachannel")
    def on_datachannel(channel):
        chunks = {}
        img_obj = ImageProcessing()
        knn_obj = KNN()

        @ channel.on("message")
        async def on_message(message):
            jsonChunk = json.loads(message)
            programPhase = jsonChunk["programPhase"]
            if programPhase == 2:
                coords = []
                keys = []
                cameraData = jsonChunk["cameraData"]
                for data in cameraData:
                    coords.append(data["coords"])
                    keys.append(data["key"])
                knn_obj.fit(coords, keys)
            else:
                keyIndex = jsonChunk["keyIndex"]
                isLast = jsonChunk["isLast"]
                frameChunk = jsonChunk["frameChunk"]
                keyTime = jsonChunk["keyTime"]
                key = jsonChunk["key"]
                if isLast == True:  # Si es el ultimo chunk se procede a reconstruir la imagen
                    # Si es primera vez se crea entreada, sino se añade el valor al existente
                    chunks.setdefault(keyIndex, []).append(frameChunk)
                    keyImg = img_obj.reconstructImage(chunks[keyIndex])
                    keyResults = img_obj.getKeyCoords(keyImg, key, keyTime)
                    if programPhase == 0:
                        keyResults["keyIndex"] = keyIndex
                        channel.send(json.dumps(keyResults))
                    else:
                        keyTest = keyResults["coords"]
                        #height, width, channels = keyImg.shape
                        #cv2.circle(keyImg, (int(keyTest[0] * width), int(keyTest[1] * height)), 5, (0, 0, 255) , 2)
                        #cv2.imshow("Image", keyImg)
                        #cv2.waitKey(1)
                        keyPred = knn_obj.predict([keyTest])[0]
                        #print(keyPred)
                        if keyPred != key:
                            keyResults["error"] = "Tecla presionada con el dedo incorrecto"
                            keyResults["keyIndex"] = keyIndex
                        #print(keyResults)
                        channel.send(json.dumps(keyResults))
                    del(chunks[keyIndex])
                        
                else:
                    chunks.setdefault(keyIndex, []).append(frameChunk)

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
