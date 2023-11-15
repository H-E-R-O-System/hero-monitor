import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from getPipeData import get_pipe_data
import cv2
from pygame import Rect
import numpy as np

base_options = python.BaseOptions(model_asset_path='face_landmarker_v2_with_blendshapes.task')
options = vision.FaceLandmarkerOptions(base_options=base_options, output_face_blendshapes=True,
                                       output_facial_transformation_matrixes=True, num_faces=1, )
detector = vision.FaceLandmarker.create_from_options(options)


img_file = "Sample_Images/Ben Glasses.png"
img_array = cv2.cvtColor(cv2.imread(img_file), cv2.COLOR_BGR2RGB)
img = mp.Image(image_format=mp.ImageFormat.SRGB, data=img_array)

# img_array = img.numpy_view()
test_cloud, blend, _ = get_pipe_data(detector, img)

test_cloud *= -1
test_cloud[:, 0] *= img_array.shape[1]
test_cloud[:, 1] *= img_array.shape[0]

max_x, min_x = max(test_cloud[:, 0]), min(test_cloud[:, 0])
max_y, min_y = max(test_cloud[:, 1]), min(test_cloud[:, 1])

# create bounding box of face
bbox = np.asarray([min_x, min_y, max_x-min_x, max_y-min_y], dtype=np.int16)
face_rect = Rect(bbox).scale_by(1.4, 1.4)