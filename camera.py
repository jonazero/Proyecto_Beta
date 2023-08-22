import numpy as np
import base64
import cv2
import os
from helpers import json2dic
from mediapipe.python.solutions import hands as mp_hands


class ImageProcessing():
    def __init__(self) -> None:
        self.mp_hands = mp_hands.Hands(static_image_mode=False,
                                       max_num_hands=2,
                                       min_detection_confidence=0.5,
                                       min_tracking_confidence=0.5,
                                       model_complexity=1)
        self.key_distribution = json2dic("src/querty.json")

    def reconstructImage(self, chunks):
        try:
            data = ''.join(chunks)
            encoded_data = data.split(",")[1]
            decoded_data = base64.b64decode(encoded_data)
            image_array = np.frombuffer(decoded_data, dtype=np.uint8)
            image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            image = cv2.flip(image, -1)
            return image
        except Exception as e:
            print(f"Error during image reconstruction: {e}")
            return None

    def getMediapipeResults(self, image):
        try:
            results = self.mp_hands.process(image)
            return results
        except Exception as e:
            print(f"Error during Mediapipe processing: {e}")
            return {"error": e}

    def getKeyCoords(self, image, key, time):
        results = self.getMediapipeResults(image)
        if results.multi_hand_landmarks:
            for idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
                mano = results.multi_handedness[idx].classification[0].label
                if key in self.key_distribution[mano]:
                    key_coord = {"key": key,
                                 "coords": [hand_landmarks.landmark[self.key_distribution[mano][key]].x,
                                            hand_landmarks.landmark[self.key_distribution[mano][key]].y],
                                 "time": time}
                    if key_coord:
                        return key_coord
                    else:
                        message = {
                            "key": key, "error": "El sistema no pudo identificar las manos. Por favor verifique que la cámara esté enfocando el teclado."}
                        return message
        else:
            message = {
                "key": key, "error": "El sistema no pudo identificar las manos. Por favor verifique que la cámara esté enfocando el teclado."}
            return message
