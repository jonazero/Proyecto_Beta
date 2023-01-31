from aiortc import MediaStreamTrack
from av import VideoFrame
from src.jsontools import json2dic, dic2json
import mediapipe as mp
import asyncio
import cv2
import numpy as np

dim = (960, 720)
mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands
mp_drawing_styles = mp.solutions.drawing_styles
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=2,
    min_detection_confidence=0.5, min_tracking_confidence=0.5, model_complexity=1)

dis = json2dic('./src/key_distribution.json')


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
        if data == "b1":
            print("guardando informacion de los dedos malos")
            for data in self.coords:
                self.coords[data] = np.divide(
                    self.coords[data], self.coords[data][3]).tolist()
            dic2json("./src/coords_b1.json", self.coords)
            return
        if data == "b2":
            print("guardando informacion de los dedos buenos")
            for data in self.coords:
                self.coords[data] = np.divide(
                    self.coords[data], self.coords[data][3]).tolist()
            dic2json("./src/coords_b.json", self.coords)
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
