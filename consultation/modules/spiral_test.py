import numpy as np
import pygame as pg
import pandas as pd
import os
import time

from consultation.touch_screen import TouchScreen, GameObjects
from consultation.screen import Colours
from consultation.display_screen import DisplayScreen


class SpiralTest:
    def __init__(self, turns, size=(1024, 600), touch_size=(600, 600), parent=None):
        self.parent = parent

        if parent:
            self.display_size = parent.display_size
            self.bottom_screen = parent.bottom_screen
            self.top_screen = parent.top_screen
        else:
            self.display_size = pg.Vector2(size)
            self.bottom_screen = pg.display.set_mode(self.display_size)
            self.top_screen = None

        self.display_screen = DisplayScreen(self.display_size)
        self.display_screen.instruction = "Start in the center"

        self.touch_size = touch_size
        self.touch_screen = TouchScreen(touch_size, colour=Colours.white)

        if parent:
            self.display_screen.avatar = parent.display_screen.avatar
            self.touch_screen.sprites = GameObjects([parent.quit_button])

        self.display_screen.update()

        self.target_coords = None
        self.load_surface(size=touch_size, turns=turns)

        self.touch_offset = (self.display_size - self.touch_size) / 2
        self.coord_idx = 0

        self.running = True

        self.spiral_data = np.zeros((5, 0))
        self.spiral_started = False
        self.spiral_finished = False

    def update_display(self):
        if self.parent:
            self.top_screen.blit(self.display_screen.get_surface(), (0, 0))

        self.bottom_screen.blit(self.touch_screen.get_surface(), self.touch_offset)
        pg.display.flip()

    def get_closest_coord_2(self, pos):
        distances = np.linalg.norm(self.target_coords - pos, axis=1)
        closest_idx = np.where(distances == min(distances))[0]
        if len(closest_idx) > 1:
            print("Clash")
            if self.coord_idx in closest_idx:
                ...
            closest_idx = closest_idx[0]
        else:
            closest_idx = closest_idx[0]
        close_coord = self.target_coords[closest_idx, :]
        return closest_idx, close_coord, min(distances)

    def load_surface(self, size=(580, 580), turns=3, clockwise=True):
        # Create spiral of diameter 1, with midpoint at (0.5, 0.5)
        n = 100  # Number of points to approximate spiral
        b = 0.5 / (2 * np.pi)  # Do not alter, ensures the scale is correct
        theta = np.linspace(0, 2 * np.pi, n)  # Spiral parametrised by theta
        x = (b * theta) * np.cos(turns * theta)  # x component of coordinate
        y = (b * theta) * np.sin(turns * theta)  # y component of coordinate
        points = np.array(([x + 0.5, y + 0.5])).transpose()  # spiral coordinates: Nx2 np array (N is number of points)

        # Scale to the size of the surface
        points = np.array([points[:, 0] * size[0], (points[:, 1]) * size[1]]).transpose()  # Scale to size of surface

        # Apply additional options
        if not clockwise:
            points[:, 1] = (size[1] - points[:, 1])

        pg.draw.lines(self.touch_screen.base_surface, Colours.black.value, False, points, width=3)
        self.target_coords = points

    def create_dataframe(self):
        return pd.DataFrame(data=self.spiral_data.transpose(),
                            columns=["rel_pos_x", "rel_pos_y", "theta", "error", "time"])

    def get_relative_mose_pos(self):
        if self.parent:
            pos = pg.Vector2(self.parent.get_relative_mose_pos()) - self.touch_offset
        else:
            pos = pg.Vector2(pg.mouse.get_pos()) - self.touch_offset

        return pos

    def entry_sequence(self):
        self.update_display()
        if self.parent:
            self.parent.speak_text("Please trace the spiral, starting from the center", visual=False)

    def exit_sequence(self):
        self.update_display()
        if self.parent:
            self.parent.speak_text("Thank you for completing the spiral test", visual=False)

    def loop(self):
        self.entry_sequence()
        start_time = time.perf_counter()

        while self.running:
            for event in pg.event.get():
                if event.type == pg.MOUSEBUTTONDOWN and not self.spiral_started:
                    rel_pos = self.get_relative_mose_pos()

                    data = np.expand_dims([*rel_pos, np.arctan2(*rel_pos), 0, 0], axis=1)
                    self.spiral_data = np.append(self.spiral_data, data, axis=1)
                    start_time = time.perf_counter()
                    self.spiral_started = True

                elif event.type == pg.MOUSEMOTION and self.spiral_started:
                    pos = self.get_relative_mose_pos()
                    idx, coord, error = self.get_closest_coord_2(np.array(pos))
                    data = np.expand_dims([*pos, np.arctan2(*pos), error, time.perf_counter() - start_time], axis=1)
                    self.spiral_data = np.append(self.spiral_data, data, axis=1)

                    # self.touch_screen.refresh()
                    if idx - self.coord_idx == 1:
                        pg.draw.line(self.touch_screen.base_surface, Colours.red.value,
                                     self.target_coords[self.coord_idx, :], self.target_coords[idx, :], width=3)
                        self.coord_idx += 1

                        if self.coord_idx == len(self.target_coords) - 1:
                            self.spiral_finished = True
                        self.update_display()

                elif event.type == pg.MOUSEBUTTONUP and self.spiral_finished:
                    self.running = False

                elif event.type == pg.KEYDOWN:
                    if event.key == pg.K_x:
                        if self.parent:
                            self.parent.take_screenshot()

                elif event.type == pg.QUIT:
                    self.running = False

        self.exit_sequence()


if __name__ == "__main__":
    # os.chdir("/Users/benhoskings/Documents/Projects/hero-monitor")
    # os.chdir('/Users/Thinkpad/Desktop/Warwick/hero-monitor')
    os.chdir("/Users/benhoskings/Documents/Pycharm/Hero_Monitor")

    pg.init()
    spiral_test = SpiralTest(turns=3, touch_size=(600, 600))
    spiral_test.loop()  # optionally extract data from here as array
    # spiral_data = spiral_test.create_dataframe()
    # spiral_data.to_csv('spiraldata.csv', index=False)
    # print(spiral_data.head(5))
