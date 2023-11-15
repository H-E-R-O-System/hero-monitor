import numpy as np


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

    except IndexError:
        landArray, blend_scores, pose_matrix = None, None, None

    return landArray, blend_scores, pose_matrix

