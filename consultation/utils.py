import cv2
import datetime
import pygame as pg
import numpy as np
import json
from datetime import date, datetime


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