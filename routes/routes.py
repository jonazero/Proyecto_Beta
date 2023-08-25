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
from database.dict import query_database
from models.dictionary import Base
from helpers import generate_chars_probability, generate_sequences_probability, lists2tuples, lists2TimeTuples
import json
import asyncio
import os
import asyncio
import cv2
import random
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

async def query_db_words(queryword):
    query_string = "SELECT word FROM words WHERE word LIKE '%"
    query_string += queryword
    query_string += f"' LIMIT {100}"
    query_string = f"SELECT word FROM ({query_string}) AS subconsulta ORDER BY RAND () LIMIT 1;"
    result = query_database(query_string)
    if result:
        print("llegue", result[0])
        return result[0][0]




@routes.post("/words/")
async def words(data: ArrayRequest):
    key_list = data.key_list
    pairs = data.pairs
    chars = data.chars
    starting_text = ["El", "La", "Mi", "Ella",
                 "Había", "Una", "Su", "Sus", "Ellos", "Las", "Los", "De"]
    random.shuffle(starting_text)
    char_tuples = lists2tuples(key_list)
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
    print("este es las data: ", key_list)
    print("este es las secuencias unicas y con la diferencia de tiempo: ", seqt_tuples)
    print("este es las letras a usar: ", char_errors)
    print("estas son las secuencias a usar: ", seq_errors)
    print("este es practice_words: ", practice_words)
    try:
        oraciones = generateSentences(practice_words, starting_text)
        oraciones_minusculas = [palabra.lower() for palabra in oraciones]
        return JSONResponse(content={'oraciones': oraciones_minusculas})
    except:
        for i, palabra in practice_words:
            palabra[i] = palabra[i].lower()
        return JSONResponse(content={'oraciones': practice_words})
    #Implementar if para no consultar la base de datos
    
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
                    benchmark_keys = jsonchunks["benchmark_keys"]
                    camera_keys = jsonchunks["camera_keys"]
                    phrase = jsonchunks["phrase"]
                    coords = [sublist[1] for sublist in camera_keys]
                    keys = [sublist[0] for sublist in camera_keys]
                    test = [sublist[1] for sublist in benchmark_keys]
                    knn_obj.fit(coords, keys)
                    y_pred = knn_obj.predict(test)
                    for i, value in enumerate(phrase):
                        if (value == y_pred[i]):
                            camera_keys.append(value)
                        else:
                            y_pred[i] = None
                    for i, value in enumerate(y_pred):
                        if value == None:
                            test[i] = None
                            benchmark_keys[i][1] = None
                    channel.send(json.dumps({"flag" : 1, "benchmark_keys": benchmark_keys}))       
                    return

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
                    #cv2.imshow("Image", img)
                    #cv2.waitKey(1)
                    results = img_obj.getKeyCoords(img, key, time)
                    print(results)
                    if results is None:
                        results = {}
                        results["error"] = "Error: tecla presionada con el dedo incorrecto"
                    elif ("error" in results):
                        kd.clear()
                    elif status == 2:
                        test = results["coords"]
                        pred = knn_obj.predict([test])
                        if pred[0] != key:
                            print("entre")
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
