import cv2
import asyncio
import mediapipe as mp
import time
import threading
import os
import numpy as np
import json
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
    static_image_mode=False,
    max_num_hands=2,
    min_detection_confidence=0.5, min_tracking_confidence=0.5, model_complexity=1)


dis = json2dic('./src/key_distribution.json')

threads = []
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

GOOGLE_CLIENT_ID = getenv("GOOGLE_CLIENT_ID")
GOOGLE_SECRET = getenv("GOOGLE_SECRET")

SSO = GoogleSSO(client_id=GOOGLE_CLIENT_ID, client_secret=GOOGLE_SECRET,
                redirect_uri="http://localhost:8000/camara", allow_insecure_http=True, use_state=False)


executor = ThreadPoolExecutor(max_workers=8)

dim = (960, 720)


class VideoTransformTrack(MediaStreamTrack):
    kind = "video"
    coords = {}

    def __init__(self, track, transform) -> None:
        super().__init__()
        self.track = track
        self.transform = transform

    async def recv(self):
        frame = await self.track.recv()
        img = frame.to_ndarray(format="bgr24")
        img = cv2.cvtColor(cv2.flip(img, 1), cv2.COLOR_BGR2RGB)
        if self.coords and self.transform == True:
            for data in self.coords:
                img = cv2.circle(
                    img, (int(self.coords[data][0] * frame.width), int(self.coords[data][1] * frame.height)), 2, (255, 0, 0), 2)
        nf = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        nf = VideoFrame.from_ndarray(nf, format="bgr24")
        nf.pts = frame.pts
        nf.time_base = frame.time_base
        return nf

    async def get_delayed_frame(self):
        await asyncio.sleep(0.15)
        frame = await self.track.recv()
        return frame

    async def set_keys(self, data):
        frame = await self.get_delayed_frame()
        frame = frame.to_ndarray(format="bgr24")
        frame = cv2.cvtColor(cv2.flip(frame, 1), cv2.COLOR_BGR2RGB)
        frame = cv2.resize(frame, dim, interpolation=cv2.INTER_AREA)
        results = hands.process(frame)
        if data == "Escape":
            for data in self.coords:
                self.coords[data] = np.divide(
                    self.coords[data], self.coords[data][3]).tolist()
            dic2json("./src/coords.json", self.coords)
            return
        if results.multi_hand_landmarks:
            for idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
                mano = results.multi_handedness[idx].classification[0].label
                mp_drawing.draw_landmarks(
                    frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                if data in dis[mano]:
                    if data in self.coords:
                        self.coords[data] = np.add(self.coords[data], [hand_landmarks.landmark[dis[mano][data]].x,
                                                                       hand_landmarks.landmark[dis[mano][data]].y, hand_landmarks.landmark[dis[mano][data]].z, 1]).tolist()
                    else:
                        self.coords[data] = ([hand_landmarks.landmark[dis[mano][data]].x,
                                              hand_landmarks.landmark[dis[mano][data]].y, hand_landmarks.landmark[dis[mano][data]].z, 1])

        else:
            return {"error": True, "key": data, "first": True, "error_name": "Error de identificacion de manos"}
        return {"error": False, "key": data, "first": True, "error_name": None}

    async def test_keys(self, data):
        frame = await self.get_delayed_frame()
        frame = frame.to_ndarray(format="bgr24")
        frame = cv2.cvtColor(cv2.flip(frame, 1), cv2.COLOR_BGR2RGB)
        frame = cv2.resize(frame, dim, interpolation=cv2.INTER_AREA)
        results = hands.process(frame)
        # cv2.imwrite('c1.png', frame)
        if data == " ":
            return {"key": data, "first": False, "error_name": None, "error": False}
        elif results.multi_hand_landmarks:
            for idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
                mano = results.multi_handedness[idx].classification[0].label
                if data in dis[mano]:
                    if abs(hand_landmarks.landmark[dis[mano][data]].x - self.coords[data][0]) < 0.025 and abs(hand_landmarks.landmark[dis[mano][data]].y - self.coords[data][1]) < 0.025:
                        return {"key": data, "first": False, "error_name": None, "error": False}
                    else:
                        return {"error": True, "key": data, "first": False, "error_name": "No se identifico el dedo"}
        else:
            return {"error": True}


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


@ app.post("/offer_cv")
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


@ app.on_event("shutdown")
async def on_shutdown():
    # Close peer connections
    coros = [pc.close() for pc in pcs]
    await asyncio.gather(*coros)
    pcs.clear()
