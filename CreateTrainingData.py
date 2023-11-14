
import numpy as np
import cv2
import os.path
from scipy.io import savemat
from tqdm import tqdm
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from MediaPipeData import getMediapipeData

fileNames = ["aro", "val", "exp", "lnd"]
basePath = "/Users/benhoskings/Documents/Emotion Recognition/Datasets/AffectNet/Data/train_set"
savePathBase = "/Users/benhoskings/Documents/Emotion Recognition/Datasets/AffectNet/Data/train_set/matlab"
emotions = ["Neutral", "Happy", "Sad", "Surprise", "Fear", "Disgust", "Anger", "Contempt"]
varNames = ["Arousal", "Valence", "Expression", "Landmarks"]
emotionDict = dict(zip(range(9), emotions))
varNameDict = dict(zip(fileNames, varNames))
nameCount = dict(zip(emotions, [0 for _ in range(len(emotions))]))


base_options = python.BaseOptions(model_asset_path='face_landmarker.task')
options = vision.FaceLandmarkerOptions(base_options=base_options,
                                       output_face_blendshapes=True,
                                       output_facial_transformation_matrixes=True,
                                       num_faces=1)
detector = vision.FaceLandmarker.create_from_options(options)

# STEP 3: Load the input image.

def getNumString(num, count=4):
    return f"{'0' * (count-1)}{num}"[-count:]

# 414796
failCount = 0
for i in tqdm(range(414796)):
    subjectData = {}
    for label in fileNames:
        file = f"{i}_{label}.npy"
        try:
            data = np.load(os.path.join(basePath, "annotations", file))
            if label == "exp":
                data = emotionDict[int(data)]
        except:
            data = "None"

        subjectData[varNameDict[label]] = data

    try:
        emotionIdx = nameCount[subjectData["Expression"]]
        imagePath = os.path.join(savePathBase, subjectData["Expression"], f"{getNumString(emotionIdx, 6)}.png")
        image = mp.Image.create_from_file(imagePath)

        # STEP 4: Detect face landmarks from the input image.
        data = getMediapipeData(image, detector)

        subjectData["Landmarks_MP"] = data["Landmarks"]
        subjectData["AUs"] = data["AUs"]
        subjectData["Pose_Matrix"] = data["Pose_Matrix"]

        savePath = os.path.join(savePathBase, subjectData["Expression"], f"{getNumString(emotionIdx, 6)}.mat")
        savemat(savePath, subjectData)
        nameCount[subjectData["Expression"]] = emotionIdx + 1

    except KeyError as e:
        # print(f"{i} failed to load")
        failCount += 1

    except IndexError as e:
        emotionIdx = nameCount[subjectData["Expression"]]
        imagePath = os.path.join(savePathBase, subjectData["Expression"], f"{getNumString(emotionIdx, 6)}.png")
        print(imagePath)

print(failCount)
# fail count is 127146
