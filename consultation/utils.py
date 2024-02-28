import cv2
import datetime
import pygame as pg


def take_screenshot(screen, filename=None):
    print("Taking Screenshot")
    img_array = pg.surfarray.array3d(screen)
    img_array = cv2.transpose(img_array)
    img_array = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
    if filename is None:
        filename = datetime.datetime.now()
    cv2.imwrite(f"screenshots/{filename}.png", img_array)