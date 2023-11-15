import time

import numpy as np
import pygame as pg

smile_1 = np.array([
    #1  2  3  4  5  6  7  8  9  10 11 12 13 14 15 16
    [0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0],  # 1
    [0, 0, 0, 1, 1, 2, 2, 2, 2, 2, 2, 1, 1, 0, 0, 0],  # 2
    [0, 0, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 0, 0],  # 3
    [0, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 0],  # 4
    [0, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 0],  # 5
    [1, 2, 2, 2, 1, 1, 2, 2, 2, 2, 1, 1, 2, 2, 2, 1],  # 6
    [1, 2, 2, 2, 1, 1, 2, 2, 2, 2, 1, 1, 2, 2, 2, 1],  # 7
    [1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1],  # 8
    [1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1],  # 9
    [1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1],  # 10
    [1, 2, 2, 2, 2, 1, 2, 2, 2, 2, 1, 2, 2, 2, 2, 1],  # 11
    [0, 1, 2, 2, 2, 2, 1, 1, 1, 1, 2, 2, 2, 2, 1, 0],  # 12
    [0, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 0],  # 13
    [0, 0, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 0, 0],  # 14
    [0, 0, 0, 1, 1, 2, 2, 2, 2, 2, 2, 1, 1, 0, 0, 0],  # 15
    [0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0],  # 16
])

smile_2 = np.array([
    #1  2  3  4  5  6  7  8  9  10 11 12 13 14 15 16
    [0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0],  # 1
    [0, 0, 0, 1, 1, 2, 2, 2, 2, 2, 2, 1, 1, 0, 0, 0],  # 2
    [0, 0, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 0, 0],  # 3
    [0, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 0],  # 4
    [0, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 0],  # 5
    [1, 2, 2, 2, 1, 1, 2, 2, 2, 2, 1, 1, 2, 2, 2, 1],  # 6
    [1, 2, 2, 2, 1, 1, 2, 2, 2, 2, 1, 1, 2, 2, 2, 1],  # 7
    [1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1],  # 8
    [1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1],  # 9
    [1, 2, 2, 2, 2, 2, 1, 1, 1, 1, 2, 2, 2, 2, 2, 1],  # 10
    [1, 2, 2, 2, 2, 1, 2, 2, 2, 2, 1, 2, 2, 2, 2, 1],  # 11
    [0, 1, 2, 2, 2, 2, 1, 1, 1, 1, 2, 2, 2, 2, 1, 0],  # 12
    [0, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 0],  # 13
    [0, 0, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 0, 0],  # 14
    [0, 0, 0, 1, 1, 2, 2, 2, 2, 2, 2, 1, 1, 0, 0, 0],  # 15
    [0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0],  # 16
])

smile_1_rgb = np.ones((16, 16, 4)) * 255
smile_2_rgb = np.ones((16, 16, 4)) * 255

# 1 corresponds to black
# 2 corresponds to face colour
face_colour = [244, 195, 67, 255]

smile_1_rgb[smile_1.transpose() == 1, :] = [0, 0, 0, 255]
smile_1_rgb[smile_1.transpose() == 2, :] = face_colour

smile_2_rgb[smile_2.transpose() == 1, :] = [0, 0, 0, 255]
smile_2_rgb[smile_2.transpose() == 2, :] = face_colour

base_surf = pg.display.set_mode((256, 256))
smile_surf_1 = pg.surfarray.make_surface(smile_1_rgb[:, :, :3])
smile_surf_2 = pg.surfarray.make_surface(smile_2_rgb[:, :, :3])

smiles = [pg.transform.scale_by(surf, 16) for surf in [smile_surf_1, smile_surf_2]]

idx = False
while True:
    base_surf.blit(smiles[idx], (0, 0))
    pg.display.flip()
    pg.event.pump()
    idx = not idx
    time.sleep(0.2)
