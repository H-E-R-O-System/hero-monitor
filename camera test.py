# import sys
# import time
# import cv2
# import numpy as np
# import pygame as pg
# import pygame.camera
#
#
# def update_screen(base, screen, text):
#     screen.refresh()
#     # add text to middle
#     middle = pg.Vector2(screen.surface.get_size()) / 2
#     screen.addText(text, middle, location=BlitLocation.centre)
#     base.blit(screen.surface, (0, 0))
#     pg.display.update()
#
#
# pg.init()
# pygame.camera.init()
# face_cam = pygame.camera.Camera()
# face_cam.start()
# cam_size = face_cam.get_size()
# face_cam.start()
#
# model = TrainedInceptionResnetV2.load_model()
# class_names = ["Anger", "Contempt", "Disgust", "Happy", "Neutral", "Fear", "Sad", "Surprise"]
#
# base_screen = pg.display.set_mode((1024, 600))
# screen_center = pg.Vector2(base_screen.get_size()) / 2
# base_screen.fill(pg.Color(255, 255, 255))
# font = pg.font.Font("Consultation/Fonts/calibri-regular.ttf", size=50)
#
# consult_screen = ConsultationScreen(base_screen.get_size(), font)
#
# pg.event.pump()
#
# t1_photo = time.monotonic()
# photo_idx = 0
# t1_process = time.monotonic()
#
# # N_Samples, W, H, D
# img_array = np.empty((cam_size[0], cam_size[1], 3), dtype=np.uint8)
# webcam_array = np.zeros((2, 299, 299, 3), dtype=np.uint8)
#
# running = True
# while running:
#     for event in pg.event.get():
#         if event.type == pg.QUIT:
#             face_cam.stop()
#             pg.quit()
#             sys.exit()
#
#     t2 = time.monotonic()
#     if t2 - t1_photo > 0.5:
#         t1_photo = time.monotonic()
#         # every 0.5s take photo
#         image_surf = face_cam.get_image()
#
#         consult_screen.image = image_surf.copy()
#         consult_screen.update()
#
#         base_screen.blit(consult_screen.touch_screen.surface, (0, 0))
#         pg.display.update()
#
#         img_array = pg.surfarray.pixels3d(image_surf)
#         webcam_array[photo_idx, :, :, :] = cv2.resize(img_array, (299, 299))
#         photo_idx = (photo_idx + 1) % 2
#         print("Take photo")
#
#     if t2 - t1_process > 1:
#         t1_process = time.monotonic()
#         print(webcam_array[0, 100, 200, :])
#         net_scores = model.predict(webcam_array)
#         for frame_idx in range(net_scores.shape[0]):
#             print(net_scores[frame_idx, :])
#             print(class_names[np.argmax(net_scores[frame_idx, :])])
#
#         consult_screen.emotion = class_names[np.argmax(net_scores[0, :])]
#         consult_screen.update()
#         base_screen.blit(consult_screen.touch_screen.surface, (0, 0))
#         pg.display.update()
def list_ports():
    """
    Test the ports and returns a tuple with the available ports
    and the ones that are working.
    """
    is_working = True
    dev_port = 0
    working_ports = []
    available_ports = []
    while is_working:
        camera = cv2.VideoCapture(dev_port)
        if not camera.isOpened():
            is_working = False
            print("Port %s is not working." %dev_port)
        else:
            is_reading, img = camera.read()
            w = camera.get(3)
            h = camera.get(4)
            if is_reading:
                print("Port %s is working and reads images (%s x %s)" %(dev_port,h,w))
                working_ports.append(dev_port)
            else:
                print("Port %s for camera ( %s x %s) is present but does not reads." %(dev_port,h,w))
                available_ports.append(dev_port)
        dev_port +=1

    return available_ports, working_ports

import cv2

print(list_ports())
image_size = (1280, 720)
cap = cv2.VideoCapture(0)
cap.set(3,image_size[0])
cap.set(4,image_size[1])

fourcc = cv2.VideoWriter_fourcc(*'MP4V')
out = cv2.VideoWriter('affective.mp4', fourcc, 20.0, image_size)

while(True):
    ret, frame = cap.read()
    out.write(frame)
    cv2.imshow('frame', frame)
    c = cv2.waitKey(1)
    if c & 0xFF == ord('q'):
        break

cap.release()
out.release()
cv2.destroyAllWindows()