import numpy as np


def getFaceLandmarks(result):
    landmarks = result.face_landmarks[0]

    landArray = np.zeros((len(landmarks), 3))
    for idx, coord in enumerate(landmarks):
        landArray[idx, :] = [coord.x, coord.y, coord.z]

    # face_landmarks_proto = landmark_pb2.NormalizedLandmarkList()
    # face_landmarks_proto.landmark.extend([
    #     landmark_pb2.NormalizedLandmark(x=landmark.x, y=landmark.y, z=landmark.z) for landmark in landmarks
    # ])

    return landArray

def getMediapipeData(image, detector):
    faceDetection = detector.detect(image)

    try:
        landmarks = getFaceLandmarks(faceDetection)
        blend = faceDetection.face_blendshapes[0]
        # blendNames = [face_blendshapes_category.category_name for face_blendshapes_category in blend]
        blendScores = [AU.score for AU in blend]
        # actionDict = dict(zip(blendNames, blendScores))
        poseMatrix = faceDetection.facial_transformation_matrixes
        data = {"Landmarks": landmarks, "AUs": blendScores, "Pose_Matrix": poseMatrix}

    except IndexError:
        data = {"Landmarks": "", "AUs": "", "Pose_Matrix": ""}

    return data

