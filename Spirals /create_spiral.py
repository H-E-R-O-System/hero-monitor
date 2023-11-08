import sys
import time
import pygame as pg
import numpy as np
from scipy.io import savemat
from Screen import Screen, BlitLocation

pg.init()

base_surf = pg.display.set_mode((500, 500))
base_surf.fill(pg.Color(255, 255, 255))

spiral_surface = Screen((500, 500))
spiral_surface.loadImage("spiral_image.png", pos=(250, 250), scale=pg.Vector2(0.5, 0.5),location=BlitLocation.centre)

base_surf.blit(spiral_surface.surface, (0, 0))
pg.display.flip()

spiral_coords = np.zeros((3, 0))
start_time = time.monotonic()

running = True
spiral_started = False
while running:
    for event in pg.event.get():
        if event.type == pg.MOUSEBUTTONDOWN:
            spiral_coords = np.append(spiral_coords, np.reshape([*pg.mouse.get_pos(), 0], (3, 1)), axis=1)
            start_time = time.monotonic()
            spiral_started = True

        if event.type == pg.MOUSEMOTION and spiral_started:
            spiral_coords = np.append(spiral_coords, np.reshape([*pg.mouse.get_pos(), time.monotonic() - start_time], (3, 1)), axis=1)
            spiral_surface.updatePixels(pg.mouse.get_pos())
            base_surf.blit(spiral_surface.surface, (0, 0))
            pg.display.flip()

        if event.type == pg.MOUSEBUTTONUP:
            running = False
            time.sleep(2)

savemat("Spiral_coords.mat", {"Coords":spiral_coords})
pg.quit()
sys.exit()
