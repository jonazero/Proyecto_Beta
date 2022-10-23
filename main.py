import cv2
import asyncio
import mediapipe as mp
import time
import threading
import os
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
app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/img", StaticFiles(directory="img"), name="img")
templates = Jinja2Templates(directory="templates")

mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands
mp_drawing_styles = mp.solutions.drawing_styles

hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=2,
    min_detection_confidence=0.5)

frame_img = ""
coords = json2dic('./src/coords.json')

dis = json2dic('./src/key_distribution.json')

threads = []
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

GOOGLE_CLIENT_ID = getenv("GOOGLE_CLIENT_ID")
GOOGLE_SECRET = getenv("GOOGLE_SECRET")

SSO = GoogleSSO(client_id=GOOGLE_CLIENT_ID, client_secret=GOOGLE_SECRET,
                redirect_uri="http://localhost:8000/camara", allow_insecure_http=True, use_state=False)


class VideoTransformTrack(MediaStreamTrack):
    kind = "video"

    def __init__(self, track, transform) -> None:
        super().__init__()
        self.track = track
        self.transform = transform

    async def recv(self):
        global frame_img
        frame = await self.track.recv()
        frame_img = frame

        return frame


class ThreadTestCoords(threading.Thread):
    def __init__(self, data, websocket):
        threading.Thread.__init__(self)
        self.data = data
        self.websocket = websocket

    def run(self):
        between_callback(self.data, self.websocket)


def test_key_coords(frame, coords, data):
    img = frame.to_ndarray(format="bgr24")
    img = cv2.cvtColor(cv2.flip(img, 1), cv2.COLOR_BGR2RGB)
    img.flags.writeable = False
    results = hands.process(img)
    if results.multi_hand_landmarks:
        for idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
            mano = results.multi_handedness[idx].classification[0].label
            if data in dis[mano]:
                if abs(hand_landmarks.landmark[dis[mano][data]].x -
                        coords[data][0]) < 0.025 and abs(hand_landmarks.landmark[dis[mano][data]].y -
                                                         coords[data][1]) < 0.025:
                    return True
                else:
                    return False


async def test_keys(data, websocket):
    print("LLEGUE")
    time.sleep(0.15)
    frame = frame_img.to_ndarray(format="bgr24")
    #cv2.imwrite('c1.png', frame)
    frame = cv2.cvtColor(cv2.flip(frame, 1), cv2.COLOR_BGR2RGB)
    results = hands.process(frame)
    if results.multi_hand_landmarks:
        for idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
            mano = results.multi_handedness[idx].classification[0].label
            if data in dis[mano]:
                if abs(hand_landmarks.landmark[dis[mano][data]].x - coords[data][0]) < 0.025 and abs(hand_landmarks.landmark[dis[mano][data]].y - coords[data][1]) < 0.025:
                    await websocket.send_text(data)


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


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("inicio.html", {"request": request})


@app.get("/auth/login")
async def auth_init():
    """Initialize auth and redirect"""
    return await SSO.get_login_redirect(params={"prompt": "consent", "access_type": "offline"})


@app.get("/camara")
async def camara(request: Request):
    # user = await SSO.verify_and_process(request)
    # print(user)
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/signup", response_class=HTMLResponse)
async def camara(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})


def between_callback(data, websocket):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(test_keys(data, websocket))
    loop.close()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        threads.append(ThreadTestCoords(data, websocket))
        threads.pop().start()
        #_thread = threading.Thread(target=between_callback, args=(data, websocket))
        # _thread.start()


@app.post("/offer_cv")
async def offer(params: Offer):
    offer = RTCSessionDescription(sdp=params.sdp, type=params.type)
    pc = RTCPeerConnection()
    pcs.add(pc)
    recorder = MediaBlackhole()
    relay = MediaRelay()

    @pc.on("datachannel")
    def on_datachannel(channel):
        @channel.on("message")
        def on_message(message):
            channel.send(message)

    @pc.on("connectionstatechange")
    async def on_connectionstatechange():
        print("Connection state is %s" % pc.connectionState)
        if pc.connectionState == "false":
            await pc.close()
            pcs.discard(pc)

    @pc.on("track")
    def on_track(track):
        if track.kind == "video":
            pc.addTrack(
                VideoTransformTrack(relay.subscribe(
                    track), transform=params.video_transform)
            )

        @track.on("ended")
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


@app.on_event("shutdown")
async def on_shutdown():
    # Close peer connections
    coros = [pc.close() for pc in pcs]
    await asyncio.gather(*coros)
    pcs.clear()
