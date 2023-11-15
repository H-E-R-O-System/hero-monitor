import sys
import time
import TrainedInceptionResnetV2
import cv2
import pygame as pg
import pygame.camera
from Screen import BlitLocation
import numpy as np
from ConsultationScreen import ConsultationScreen


def update_screen(base, screen, text):
    screen.refresh()
    # add text to middle
    middle = pg.Vector2(screen.surface.get_size()) / 2
    screen.addText(text, middle, location=BlitLocation.centre)
    base.blit(screen.surface, (0, 0))
    pg.display.update()


pg.init()
pygame.camera.init()
face_cam = pygame.camera.Camera()
face_cam.start()
cam_size = face_cam.get_size()
face_cam.start()

model = TrainedInceptionResnetV2.load_model()
class_names = ["Anger", "Contempt", "Disgust", "Happy", "Neutral", "Fear", "Sad", "Surprise"]

base_screen = pg.display.set_mode((1024, 600))
screen_center = pg.Vector2(base_screen.get_size()) / 2
base_screen.fill(pg.Color(255, 255, 255))
font = pg.font.Font("Consultation/Fonts/calibri-regular.ttf", size=50)

consult_screen = ConsultationScreen(base_screen.get_size(), font)

pg.event.pump()

t1_photo = time.monotonic()
photo_idx = 0
t1_process = time.monotonic()

# N_Samples, W, H, D
img_array = np.empty((cam_size[0], cam_size[1], 3), dtype=np.uint8)
webcam_array = np.zeros((2, 299, 299, 3), dtype=np.uint8)

running = True
while running:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            face_cam.stop()
            pg.quit()
            sys.exit()

    t2 = time.monotonic()
    if t2 - t1_photo > 0.5:
        t1_photo = time.monotonic()
        # every 0.5s take photo
        image_surf = face_cam.get_image()

        consult_screen.image = image_surf.copy()
        consult_screen.update()

        base_screen.blit(consult_screen.screen.surface, (0, 0))
        pg.display.update()

        img_array = pg.surfarray.pixels3d(image_surf)
        webcam_array[photo_idx, :, :, :] = cv2.resize(img_array, (299, 299))
        photo_idx = (photo_idx + 1) % 2
        print("Take photo")

    if t2 - t1_process > 1:
        t1_process = time.monotonic()
        print(webcam_array[0, 100, 200, :])
        net_scores = model.predict(webcam_array)
        for frame_idx in range(net_scores.shape[0]):
            print(net_scores[frame_idx, :])
            print(class_names[np.argmax(net_scores[frame_idx, :])])

        consult_screen.emotion = class_names[np.argmax(net_scores[0, :])]
        consult_screen.update()
        base_screen.blit(consult_screen.screen.surface, (0, 0))
        pg.display.update()
