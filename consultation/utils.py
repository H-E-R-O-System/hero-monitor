import cv2
import datetime
import pygame as pg
import numpy as np
import json
from datetime import date, datetime
from enum import Enum




def sigmoid(x):
    return


def get_pipe_data(detector, image):
    faceDetection = detector.detect(image)

    try:
        landmarks = faceDetection.face_landmarks[0]

        landArray = np.zeros((len(landmarks), 3))
        for idx, coord in enumerate(landmarks):
            landArray[idx, :] = [coord.x, coord.y, coord.z]

        blend = faceDetection.face_blendshapes[0]

        blend_scores = [AU.score for AU in blend]
        pose_matrix = faceDetection.facial_transformation_matrixes[0]

    except:
        landArray, blend_scores, pose_matrix = None, None, None

    return landArray, blend_scores, pose_matrix


def take_screenshot(screen, filename=None):
    print("Taking Screenshot")
    img_array = pg.surfarray.array3d(screen)
    img_array = cv2.transpose(img_array)
    img_array = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
    if filename is None:
        filename = datetime.datetime.now()
    cv2.imwrite(f"screenshots/{filename}.png", img_array)


class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()

        return super(NpEncoder, self).default(obj)


class Buttons(Enum):
    power = "Power"
    Home = "Home"
    vol_up = "Vol_Up"
    vol_down = "Vol_Down"
    info = "Info"


class ButtonModule:
    def __init__(self, pi=True):
        self.pi = pi
        if self.pi:
            gpiod = __import__('gpiod')

            # Define Raspberry Pi button pins
            self.button_dict = {
                4: "Power",  # Pin number 7
                17: "Home",  # Pin number 11
                23: "Vol_Up",  # Pin number 16
                27: "Vol_Down",  # Pin number 13
                22: "Info",  # Pin number 15
            }
            # LED_PIN = 17

            chip = gpiod.Chip('gpiochip4')
            # led_line = chip.get_line(LED_PIN)
            self.button_lines = [(chip.get_line(pin_num), self.button_dict[pin_num]) for pin_num in self.button_dict.keys()]
            # led_line.request(consumer="LED", type=gpiod.LINE_REQ_DIR_OUT)
            for (line, name) in self.button_lines:
                line.request(consumer="Button", type=gpiod.LINE_REQ_DIR_IN)
        else:

            self.button_dict = {
                pg.K_1: "Power",  # Pin number 7
                pg.K_2: "Home",  # Pin number 11
                pg.K_3: "Vol_Up",  # Pin number 16
                pg.K_4: "Vol_Down",  # Pin number 13
                pg.K_5: "Info",  # Pin number 15
            }

        self.states = {
            "Power": 0,  # to track the current state (on/off)
            "Home": 0,  # to track the current state (on/off)
            "Vol_Up": 0,  # to track the current state (on/off)
            "Vol_Down": 0,  # to track the current state (on/off)
            "Info": 0,  # to track the current state (on/off)
        }

        self.buttons = Buttons

    def check_pressed(self):
        if self.pi:
            for idx, (line, name) in enumerate(self.button_lines):
                button_state = line.get_value()

                self.states[name] = button_state

                if button_state and not self.states[name]:
                    print(f"{name} Pressed")
                    return self.buttons(name)

        else:
            pressed = pg.key.get_pressed()
            for val, name in self.button_dict.items():

                if pressed[val] and not self.states[name]:
                    self.states[name] = pressed[val]
                    return self.buttons(name)

                self.states[name] = pressed[val]

        return None


if __name__ == "__main__":
    pg.init()
    pg.event.pump()

    pi = False

    buttons = ButtonModule(pi=pi)

    while True:
        if not pi:
            pg.event.pump()

            pressed = buttons.check_pressed()
            if pressed:
                print(f"{pressed}!")
        else:
            pressed = buttons.check_pressed()
            if pressed:
                print(f"{pressed}!")
