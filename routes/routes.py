from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from starlette.requests import Request
from starlette.templating import Jinja2Templates
from aiortc import RTCPeerConnection, RTCSessionDescription
from src.schemas import Offer
from knn import KNN
from textgen import generateSentences
from camera import ImageProcessing
from models.dictionary import ArrayRequest
from models.user import User
from jsonwt import get_current_user_params
from database.db import engine
from database.user import update_user
from database.dict import query_database
from models.dictionary import Base
from helpers import generate_chars_probability, list2Tuples, lists2TimeTuples, generate_sequences_probability
from unidecode import unidecode
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

@routes.get("/estadisticas")
async def estadisticas(request: Request):
    return templates.TemplateResponse("estadisticas.html", {"request": request})


@routes.get("/user/params")
async def UserParams(params: User = Depends(get_current_user_params)):
    return params.keyData

@routes.get("/user/stats")
async def UserStats(params: User = Depends(get_current_user_params)):
    repeatedKeys = {'a': {'cont': 0, 'aciertos': 0}, 'b': {'cont': 0, 'aciertos': 0}, 'c': {'cont': 0, 'aciertos': 0}, 
                    'd': {'cont': 0, 'aciertos': 0}, 'e': {'cont': 0, 'aciertos': 0}, 'f': {'cont': 0, 'aciertos': 0}, 
                    'g': {'cont': 0, 'aciertos': 0}, 'h': {'cont': 0, 'aciertos': 0}, 'i': {'cont': 0, 'aciertos': 0}, 
                    'j': {'cont': 0, 'aciertos': 0}, 'k': {'cont': 0, 'aciertos': 0}, 'l': {'cont': 0, 'aciertos': 0}, 
                    'm': {'cont': 0, 'aciertos': 0}, 'n': {'cont': 0, 'aciertos': 0}, 'ñ': {'cont': 0, 'aciertos': 0},
                    'o': {'cont': 0, 'aciertos': 0}, 'p': {'cont': 0, 'aciertos': 0}, 'q': {'cont': 0, 'aciertos': 0}, 
                    'r': {'cont': 0, 'aciertos': 0}, 's': {'cont': 0, 'aciertos': 0}, 't': {'cont': 0, 'aciertos': 0}, 
                    'u': {'cont': 0, 'aciertos': 0}, 'v': {'cont': 0, 'aciertos': 0}, 'w': {'cont': 0, 'aciertos': 0}, 
                    'x': {'cont': 0, 'aciertos': 0}, 'y': {'cont': 0, 'aciertos': 0}, 'z': {'cont': 0, 'aciertos': 0}}    
    keyData = params.keyData
    keyAccuracy = []
    listKeys = []
    keyTuples = []
    averagedTuples = {}
    matriz = []
    abc = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'ñ', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
    for key in keyData:
        k = key.key
        if k.isalpha() or k == "ñ":
            if key.coords == None:
                repeatedKeys[k] = {"cont": repeatedKeys[k]["cont"] + 1, "aciertos": repeatedKeys[k]["aciertos"]}
            else:
                repeatedKeys[k] = {"cont": repeatedKeys[k]["cont"] + 1, "aciertos": repeatedKeys[k]["aciertos"] + 1}
    for key in repeatedKeys:
        keyAccuracy.append((repeatedKeys[key]["aciertos"] * 100)/repeatedKeys[key]["cont"])

    for key in keyData:
        k = key.key
        if k.isalpha():
            listKeys.append((key.key, key.coords, key.time))
    
    for i, d in enumerate(listKeys):
        if(i == len(listKeys) - 1):
            break
        if(d[1] != None and listKeys[i+1][1] != None):
            keyTuples.append((d[0], listKeys[i+1][0], listKeys[i+1][2] - d[2]))
    
    for tup in keyTuples:
        key = (tup[0], tup[1])
        value = tup[2]
        if key in averagedTuples:
            averagedTuples[key].append(value)
        else:
            averagedTuples[key] = [value]

    result = [(key[0], key[1], sum(values) / len(values)) for key, values in averagedTuples.items()]

    for _ in range(27):
        # Crear una sublista con 27 ceros
        sublista = [0] * 27
        # Agregar la sublista a la lista principal
        matriz.append(sublista)
    
    for i, r in enumerate(result):
        fila = abc.index(r[0])
        columna = abc.index(r[1])
        if abs(r[2]) < 600:
            matriz[fila][columna] = r[2]
            

    print(matriz)
  
    return matriz, keyAccuracy


@routes.post("/user/update")
async def updateUser(keyData: List[ArrayRequest], user: User = Depends(get_current_user_params)):
    return update_user(keyData, user)


async def query_db_words(queryword, limit):
    query_string = "SELECT word FROM words WHERE word LIKE '%"
    query_string += queryword
    query_string += f"' LIMIT {50}"
    query_string = f"SELECT word FROM ({query_string}) AS subconsulta ORDER BY RAND () LIMIT {limit};"
    result = query_database(query_string)
    if result:
        return [word[0] for word in result]


@routes.post("/words/")
async def words(data: List[ArrayRequest]):
    starting_text = []
    practice_words = []
    dataError = []
    dataTimeError = []
    for i, d in enumerate(data):
        if d.key.isalpha():
            dataError.append(
                {"key": d.key, 'coords': d.coords, 'time': d.time})

            if i < len(data) - 1 and d.coords is not None:
                next_data = data[i + 1]

                if next_data.key.isalpha() and next_data.coords is not None:
                    dataTimeError.append(
                        {"key": d.key, 'coords': d.coords, 'time': d.time})

    # Add a check for the last element outside the loop
    if data[-1].key.isalpha() and data[-1].coords is not None:
        dataTimeError.append(
            {"key": data[-1].key, 'coords': data[-1].coords, 'time': data[-1].time})

    random.shuffle(starting_text)
    charTuples = list2Tuples(dataError)
    timeTuples = lists2TimeTuples(dataTimeError)
    chars = generate_chars_probability(charTuples, 5)
    pairs = generate_sequences_probability(timeTuples, 5)
    if (chars is not None):
        for char_error in chars:
            response = await query_db_words(f"{char_error}%", 2)
            practice_words.append(response[0])
            starting_text.append(response[1])
    if (pairs is not None):
        frecuencia = {}
        for par in pairs:
            if par in frecuencia:
                frecuencia[par] += 1
            else:
                frecuencia[par] = 1
        pairs = [par + (count,) for par, count in frecuencia.items()]
        for tupleerror in pairs:
            response = await query_db_words(f"{tupleerror[0]+tupleerror[1]}%", 2)
            if response is not None:
                practice_words.append(response[0])
                starting_text.append(response[1])

    practice_words = [' ' + palabra for palabra in practice_words]
    try:
        oraciones = generateSentences(practice_words, starting_text)
        #oraciones = (practice_words, starting_text)
        oraciones_minusculas = [unidecode(palabra).lower(
        ) if "ñ" not in palabra else palabra.lower() for palabra in oraciones]
        return JSONResponse(content={'oraciones': oraciones_minusculas})
    except Exception as e:
        print("este fue el error: ", e)
        return JSONResponse(content={'oraciones': practice_words})


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
        gidx = None

        @ channel.on("message")
        async def on_message(message):
            nonlocal gidx
            jsonChunk = json.loads(message)
            programPhase = jsonChunk["programPhase"]
            if programPhase == 2:
                coords = []
                keys = []
                cameraData = jsonChunk["cameraData"]
                for data in cameraData:
                    coords.append(data["coords"])
                    keys.append(data["key"])
                    if gidx == None:  # Se agrega la clase tope para delimitar el teclado
                        if data["key"] == "a" or data["key"] == "q" or data["key"] == "z":
                            d = data["coords"][0] + 0.04
                            coords.append([d, data["coords"][1]])
                            keys.append("tope")
                        if data["key"] == "p" or data["key"] == "ñ" or data["key"] == "m":
                            d = data["coords"][0] - 0.04
                            coords.append([d, data["coords"][1]])
                            keys.append("tope")
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
                    keyTest = keyResults["coords"]
                    if programPhase == 0:
                        keyResults["keyIndex"] = keyIndex
                        channel.send(json.dumps(keyResults))
                    else:
                        opt = False
                        if gidx != None:
                            if gidx == keyIndex:
                                opt = True
                        gidx = keyIndex
                        keyTest = keyResults["coords"]
                        '''
                        height, width, channels = keyImg.shape
                        cv2.circle(keyImg, (int(
                            keyTest[0] * width), int(keyTest[1] * height)), 5, (255, 255, 254), 2)
                        cv2.imshow("Image", keyImg)
                        cv2.waitKey(1)
                        '''
                        if opt == False:
                            keyPred = knn_obj.predict([keyTest])[0]
                            if keyPred != key:
                                keyResults["error"] = "Tecla presionada con el dedo incorrecto"
                                keyResults["keyIndex"] = keyIndex
                        channel.send(json.dumps(keyResults))
                    del (chunks[keyIndex])

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
