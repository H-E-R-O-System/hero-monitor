import time
import pygame as pg
import numpy as np
from scipy.io import savemat
from screen import Screen, BlitLocation
import spiral_graph
import pandas as pd

pg.init()

scaling_factor = 1
turns_factor = 2.2

spiral_graph.plot_spiral(scaling_factor, turns_factor, t_max=1, num_points=1000)

base_surf = pg.display.set_mode((500, 500))
base_surf.fill(pg.Color(255, 255, 255))

spiral_surface = Screen((500, 500))

spiral_surface.loadImage("spiral_plot.png", pos=(250, 250), scale=pg.Vector2(0.5, 0.5),location=BlitLocation.centre)

base_surf.blit(spiral_surface.surface, (0, 0))
pg.display.flip()

spiral_coords = np.zeros((0, 4))
points=[]

running = True
spiral_started = False
while running:
    for event in pg.event.get():
        if event.type == pg.MOUSEBUTTONDOWN and spiral_started == False:
            newdata= np.reshape([pg.mouse.get_pos()[0]-250,pg.mouse.get_pos()[1]-250,np.arctan2(pg.mouse.get_pos()[1]-250,pg.mouse.get_pos()[0]-250), 0], (1, 4))
            spiral_coords = np.vstack([spiral_coords, newdata])
            start_time = time.monotonic()
            spiral_started = True

        if spiral_started == True:
            newdata= np.reshape([pg.mouse.get_pos()[0]-250,pg.mouse.get_pos()[1]-250 ,np.arctan2(pg.mouse.get_pos()[1]-250,pg.mouse.get_pos()[0]-250), time.monotonic() - start_time], (1, 4))
            spiral_coords = np.vstack([spiral_coords,newdata])
            base_surf.blit(spiral_surface.surface, (0, 0))
            spiral_surface.updatePixels(spiral_coords[:,2],scaling_factor,turns_factor)
            pg.display.flip()

        if event.type == pg.MOUSEBUTTONUP:
            running = False
            time.sleep(2)

columns = ['x_values', 'y_values','angles', 'time']

df = pd.DataFrame(spiral_coords, columns=columns)
print(df)


