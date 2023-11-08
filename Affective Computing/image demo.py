import pygame as pg
import mediapipe as mp
from Screen import Screen
import time

import cv2
import matplotlib.pyplot as plt
import numpy as np

img = cv2.imread("Sample_Images/Anger_01.png")
img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
print(img.shape)
fig = plt.figure()

im1 = fig.figimage(img)

plt.show()
