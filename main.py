import cv2
import asyncio
import mediapipe as mp
import time
import threading
import os
import numpy as np
from av import VideoFrame
from fastapi import FastAPI
from fastapi import FastAPI, WebSocket
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from starlette.templating import Jinja2Templates
from starlette.requests import Request
from aiortc import MediaStreamTrack, RTCPeerConnection, RTCSessionDescription
from aiortc.contrib.media import MediaRelay, MediaBlackhole
from src.schemas import Offer
from src.jsontools import json2dic, dic2json
from fastapi_sso.sso.google import GoogleSSO
from os import getenv
from concurrent.futures import ThreadPoolExecutor
app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/img", StaticFiles(directory="img"), name="img")
app.mount("/audio", StaticFiles(directory="audio"), name="audio")
templates = Jinja2Templates(directory="templates")

mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands
mp_drawing_styles = mp.solutions.drawing_styles

hands = mp_hands.Hands(
    static_image_mode=True,
    max_num_hands=2,
    min_detection_confidence=0.5, min_tracking_confidence=0.8, model_complexity=1)


dis = json2dic('./src/key_distribution.json')

threads = []
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

GOOGLE_CLIENT_ID = getenv("GOOGLE_CLIENT_ID")
GOOGLE_SECRET = getenv("GOOGLE_SECRET")

SSO = GoogleSSO(client_id=GOOGLE_CLIENT_ID, client_secret=GOOGLE_SECRET,
                redirect_uri="http://localhost:8000/camara", allow_insecure_http=True, use_state=False)


executor = ThreadPoolExecutor(max_workers=8)

dim = (960, 720)

coords = {}
first = True


class VideoTransformTrack(MediaStreamTrack):
    kind = "video"

    def __init__(self, track, transform) -> None:
        super().__init__()
        self.track = track
        self.transform = transform

    async def recv(self):
        frame = await self.track.recv()
        img = frame.to_ndarray(format="bgr24")
        img = cv2.cvtColor(cv2.flip(img, 1), cv2.COLOR_BGR2RGB)
        if coords and first == False:
            for data in coords:
                img = cv2.circle(
                    img, (int(coords[data][0] * frame.width), int(coords[data][1] * frame.height)), 2, (255, 0, 0), 2)
        nf = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        nf = VideoFrame.from_ndarray(nf, format="bgr24")
        nf.pts = frame.pts
        nf.time_base = frame.time_base
        return nf

    async def recv2(self):
        await asyncio.sleep(0.15)
        frame = await self.track.recv()
        return frame


async def set_keys(data, frame):
    global coords
    global first
    frame = frame.to_ndarray(format="bgr24")
    frame = cv2.cvtColor(cv2.flip(frame, 1), cv2.COLOR_BGR2RGB)
    frame = cv2.resize(frame, dim, interpolation=cv2.INTER_AREA)
    results = hands.process(frame)
    if data == "Escape":
        first = False
        for data in coords:
            coords[data] = np.divide(coords[data], coords[data][3]).tolist()
        dic2json("./src/coords.json", coords)
        return
    if results.multi_hand_landmarks:
        for idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
            mano = results.multi_handedness[idx].classification[0].label
            mp_drawing.draw_landmarks(
                frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            if data in dis[mano]:
                if data in coords:
                    coords[data] = np.add(coords[data], [hand_landmarks.landmark[dis[mano][data]].x,
                                                         hand_landmarks.landmark[dis[mano][data]].y, hand_landmarks.landmark[dis[mano][data]].z, 1]).tolist()
                else:
                    coords[data] = ([hand_landmarks.landmark[dis[mano][data]].x,
                                     hand_landmarks.landmark[dis[mano][data]].y, hand_landmarks.landmark[dis[mano][data]].z, 1])

    else:
        print("Enfoque la camara")


async def test_keys(data, channel, frame):
    frame = frame.to_ndarray(format="bgr24")
    frame = cv2.cvtColor(cv2.flip(frame, 1), cv2.COLOR_BGR2RGB)
    frame = cv2.resize(frame, dim, interpolation=cv2.INTER_AREA)
    results = hands.process(frame)
    # cv2.imwrite('c1.png', frame)
    if data == " ":
        channel.send(data)
    else:
        if results.multi_hand_landmarks:
            for idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
                mano = results.multi_handedness[idx].classification[0].label
                if data in dis[mano]:
                    if abs(hand_landmarks.landmark[dis[mano][data]].x - coords[data][0]) < 0.025 and abs(hand_landmarks.landmark[dis[mano][data]].y - coords[data][1]) < 0.025:
                        channel.send(data)
                    else:
                        cv2.imwrite('c1.png', frame)
                        print("Error")
        else:
            print("error")


"""
def create_local_tracks(play_from=None):
    if play_from:
        player = MediaPlayer(play_from)
        return player.video
    else:
        options = {"framerate": "60", "video_size": "1980x1080"}
        webcam = MediaPlayer("video=OBS-Camera",
                             format="dshow", options=options)
        relay = MediaRelay()
        return None, relay.subscribe(webcam.video)
"""


@ app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("inicio.html", {"request": request})


@ app.get("/auth/login")
async def auth_init():
    """Initialize auth and redirect"""
    return await SSO.get_login_redirect(params={"prompt": "consent", "access_type": "offline"})


@ app.get("/camara")
async def camara(request: Request):
    # user = await SSO.verify_and_process(request)
    # print(user)
    return templates.TemplateResponse("index.html", {"request": request})


@ app.get("/signup", response_class=HTMLResponse)
async def camara(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})


def between_callback(data, channel, frame):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(test_keys(data, channel, frame))
    loop.close()


def between_callback2(data, frame):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(set_keys(data, frame))
    loop.close()


'''
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        threads.append(ThreadTestCoords(data, websocket))
        threads.pop().start()
        # _thread = threading.Thread(target=between_callback, args=(data, websocket))
        # _thread.start()

'''


@ app.post("/offer_cv")
async def offer(params: Offer):
    offer = RTCSessionDescription(sdp=params.sdp, type=params.type)
    pc = RTCPeerConnection()
    pcs.add(pc)
    recorder = MediaBlackhole()
    relay = MediaRelay()
    obj = None

    @ pc.on("datachannel")
    def on_datachannel(channel):
        @ channel.on("message")
        async def on_message(message):
            frame = await obj.recv2()
            if first == True:
                #executor.submit(between_callback2, message, frame)
                await set_keys(message, frame)
            else:
                #executor.submit(between_callback, message, channel, frame)
                await test_keys(message, channel, frame)

    @ pc.on("connectionstatechange")
    async def on_connectionstatechange():
        print("Connection state is %s" % pc.connectionState)
        if pc.connectionState == "false":
            await pc.close()
            pcs.discard(pc)

    @ pc.on("track")
    def on_track(track):
        nonlocal obj
        if track.kind == "video":
            obj = VideoTransformTrack(relay.subscribe(
                track), transform=params.video_transform)
            pc.addTrack(obj)

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


@ app.on_event("shutdown")
async def on_shutdown():
    # Close peer connections
    coros = [pc.close() for pc in pcs]
    await asyncio.gather(*coros)
    pcs.clear()
