import numpy as np
import pygame as pg
import pandas as pd
import os
import time
import cv2

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
        self.touch_screen = TouchScreen(size, colour=Colours.white)

        if parent:
            self.display_screen.avatar = parent.display_screen.avatar
            self.touch_screen.sprites = GameObjects([parent.quit_button])

        self.display_screen.update()

        self.target_coords = None
        self.touch_offset = (self.display_size - self.touch_size) / 2
        self.load_surface(size=touch_size, turns=turns)

        self.coord_idx = 0

        self.mouse_down = False

        self.running = True

        self.spiral_data = np.zeros((7, 0))
        self.spiral_started = False
        self.spiral_finished = False

    def update_display(self):
        if self.parent:
            self.top_screen.blit(self.display_screen.get_surface(), (0, 0))

        self.bottom_screen.blit(self.touch_screen.get_surface(), (0, 0))
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

        points += np.array([self.touch_offset.x, self.touch_offset.y])

        pg.draw.lines(self.touch_screen.base_surface, Colours.black.value, False, points, width=3)
        self.target_coords = points

    def create_dataframe(self):
        return pd.DataFrame(data=self.spiral_data.transpose(),
                            columns=["pixel_x", "pixel_y", "rel_pos_x", "rel_pos_y", "theta", "error", "time"]), self.touch_size

    def get_relative_mose_pos(self):
        if self.parent:
            pos = pg.Vector2(self.parent.get_relative_mose_pos())
        else:
            pos = pg.Vector2(pg.mouse.get_pos())

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
                if event.type == pg.MOUSEBUTTONDOWN:
                    if not self.spiral_started:
                        pos = self.get_relative_mose_pos()
                        rel_pos = pos - self.display_size / 2
                        pixel_pos = pos - self.touch_offset
                        print(pixel_pos)
                        error = np.linalg.norm(np.array([pos.x, pos.y]) - self.target_coords[0, :])
                        data = np.expand_dims([*pixel_pos, *rel_pos, np.arctan2(*rel_pos), error, 0], axis=1)
                        self.spiral_data = np.append(self.spiral_data, data, axis=1)
                        start_time = time.perf_counter()
                        self.spiral_started = True

                    self.mouse_down = True

                elif event.type == pg.MOUSEMOTION and self.mouse_down:
                    pos = self.get_relative_mose_pos()
                    idx, coord, error = self.get_closest_coord_2(np.array(pos))
                    rel_pos = pos - self.display_size / 2
                    pixel_pos = pos - self.touch_offset
                    print(pixel_pos)
                    # could use pygame inbuilt Vector2 to_polar
                    data = np.expand_dims([*pixel_pos, *rel_pos, np.arctan2(*rel_pos), error, time.perf_counter() - start_time], axis=1)
                    self.spiral_data = np.append(self.spiral_data, data, axis=1)

                    # self.touch_screen.refresh()
                    if idx - self.coord_idx == 1:
                        pg.draw.line(self.touch_screen.base_surface, Colours.red.value,
                                     self.target_coords[self.coord_idx, :], self.target_coords[idx, :], width=3)
                        self.coord_idx += 1

                        if self.coord_idx == len(self.target_coords) - 1:
                            self.spiral_finished = True
                            self.running = False

                        self.update_display()

                elif event.type == pg.MOUSEBUTTONUP:
                    self.mouse_down = False

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
    spiral_test = SpiralTest(turns=3)
    spiral_test.loop()  # optionally extract data from here as array
    spiral_data, spiral_size = spiral_test.create_dataframe()
    # Spiral data is a pd dataframe that contains the coordinates
    # reconstructed image should be of size spiral_size
    print(spiral_data.head(5))
    spiral_data.to_csv('spiraldata.csv', index=False)

    # reconstruct image
    spiral_image = pg.Surface(spiral_size, pg.SRCALPHA)  # create surface of correct size
    spiral_image.fill(Colours.white.value)  # fill with white background
    # draw in lines between each point recorded
    pg.draw.lines(spiral_image, Colours.black.value, False, spiral_data[["pixel_x", "pixel_y"]].to_numpy(), width=3)

    img_array = pg.surfarray.array3d(spiral_image)  # extract the pixel data from the pygame surface
    img_array = cv2.transpose(img_array)  # transpose to switch from pg to cv2 axis
    img_array = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)  # switch from RGB (pygame) to BGR (cv2) colours
    cv2.imwrite("spiral.png", img_array)  # Save image
    print("ok")

