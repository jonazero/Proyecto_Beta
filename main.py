from tkinter.tix import Tree
from unittest import result
import cv2
from jsontools import json2dic
import key_mapping
from fastapi import FastAPI
from fastapi import FastAPI, WebSocket
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from starlette.templating import Jinja2Templates
from starlette.requests import Request
from aiortc import MediaStreamTrack, RTCPeerConnection, RTCSessionDescription
from aiortc.contrib.media import MediaPlayer, MediaRelay, MediaBlackhole
from av import VideoFrame
import asyncio
import mediapipe as mp
from src.schemas import Offer
app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands
mp_drawing_styles = mp.solutions.drawing_styles

hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=2,
    min_detection_confidence=0.5)

frame_img = ""
coords = json2dic('coords.json')


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
        '''
        img = frame.to_ndarray(format="bgr24")
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img.flags.writeable = False
        results = hands.process(img)
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(
                    img,
                    hand_landmarks,
                    mp_hands.HAND_CONNECTIONS,
                    mp_drawing_styles.get_default_hand_landmarks_style(),
                    mp_drawing_styles.get_default_hand_connections_style())
        new_frame = VideoFrame.from_ndarray(img, format="bgr24")
        new_frame.pts = frame.pts
        new_frame.time_base = frame.time_base
        cv2.destroyAllWindows()
        '''
        return frame


def test_key_coords(frame, coords, data):
    dis = json2dic('key_distribution.json')
    img = frame.to_ndarray(format="bgr24")
    img = cv2.cvtColor(cv2.flip(img, 1), cv2.COLOR_BGR2RGB)
    img.flags.writeable = False
    results = hands.process(img)
    if results.multi_hand_landmarks:
        for idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
            mano = results.multi_handedness[idx].classification[0].label
            if data in dis[mano]:
                if abs(hand_landmarks.landmark[dis[mano][data]].x -
                        coords[data][0]) < 0.030 and abs(hand_landmarks.landmark[dis[mano][data]].y -
                                                         coords[data][1]) < 0.030:
                    return True
                else:
                    return False


def create_local_tracks(play_from=None):
    if play_from:
        player = MediaPlayer(play_from)
        return player.video
    else:
        options = {"framerate": "20", "video_size": "1280x720"}
        webcam = MediaPlayer("video=Integrated Camera",
                             format="dshow", options=options)
        relay = MediaRelay()
        return None, relay.subscribe(webcam.video)


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        res = test_key_coords(frame_img, coords, data)
        if res == True:
            await websocket.send_text("Si")
        else:
            await websocket.send_text("No")


@app.post("/offer_cv")
async def offer(params: Offer):
    offer = RTCSessionDescription(sdp=params.sdp, type=params.type)
    pc = RTCPeerConnection()
    pcs.add(pc)
    recorder = MediaBlackhole()
    relay = MediaRelay()

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
    coros = [pc.close() for pc in pcs]
    await asyncio.gather(*coros)
    pcs.clear()
