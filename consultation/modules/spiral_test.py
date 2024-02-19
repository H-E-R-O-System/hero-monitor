import numpy as np
import pygame as pg
import pandas as pd
import os
import time
import cv2

from consultation.touch_screen import TouchScreen, GameObjects
from consultation.screen import Colours
from consultation.display_screen import DisplayScreen
from consultation.spiral_data_graphing import DataAnalytics, FeatureEngineering


class SpiralTest:
    def __init__(self, turns, size=(1024, 600), touch_size=(400, 400), parent=None):
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

        self.target_coords = None
        self.theta_vals = None

        self.plot_data = None
        self.turns = turns
        self.image_offset = (self.display_size - self.touch_size) / 2
        self.center_offset = self.display_size / 2
        self.load_surface(size=touch_size, turns=turns)

        self.coord_idx = 0

        self.mouse_down = False

        self.running = True

        self.mouse_positions = np.zeros((0, 4))
        self.spiral_data = np.zeros((7, 0))
        self.spiral_started = False
        self.spiral_finished = False
        self.prev_pos = None
        self.turns = 0

        self.output = None

    def update_display(self):
        if self.parent:
            self.top_screen.blit(self.display_screen.get_surface(), (0, 0))

        self.bottom_screen.blit(self.touch_screen.get_surface(), (0, 0))
        pg.display.flip()

    def get_closest_coord_2(self, pos):
        distances = np.linalg.norm(self.target_coords - pos, axis=1)
        closest_idx = np.where(distances == min(distances))[0]
        if len(closest_idx) > 1:
            if self.coord_idx in closest_idx:
                ...
            closest_idx = closest_idx[0]
        else:
            closest_idx = closest_idx[0]
        close_coord = self.target_coords[closest_idx, :]
        return closest_idx, close_coord, min(distances)

    def load_surface(self, size=(580, 580), turns=3, clockwise=True):
        # Create spiral of diameter 1, with midpoint at (0.5, 0.5)
        n = 500  # Number of points to approximate spiral
        b = 0.5 / (2 * np.pi)  # Do not alter, ensures the scale is correct
        theta =np.sqrt(np.linspace(0, (2 * np.pi)**2, n)) # Spiral parametrised by theta
        self.theta_vals = theta * turns
        x = (b * theta) * np.cos(turns * theta)  # x component of coordinate
        y = (b * theta) * np.sin(turns * theta)  # y component of coordinate
        points = np.array(([x + 0.5, y + 0.5])).transpose()  # spiral coordinates: Nx2 np array (N is number of points)

        # Scale to the size of the surface
        points = np.array([points[:, 0] * size[0], (points[:, 1]) * size[1]]).transpose()  # Scale to size of surface

        # Apply additional options
        if not clockwise:
            points[:, 1] = (size[1] - points[:, 1])

        center_points = points - pg.Vector2(size)/2

        plot_data = np.concatenate([
            np.expand_dims(center_points[:, 0], axis=1), np.expand_dims(center_points[:, 1], axis=1), np.expand_dims(theta*turns, axis=1),
            np.expand_dims(np.linalg.norm(np.concatenate([np.expand_dims(center_points[:, 0], axis=1),
                                                          np.expand_dims(center_points[:, 1], axis=1)], axis=1),
                                          axis=1), axis=1)], axis=1)

        self.plot_data = pd.DataFrame(plot_data, columns=["x", "y", "theta", "mag"])

        points += np.array([self.image_offset.x, self.image_offset.y])

        pg.draw.lines(self.touch_screen.base_surface, Colours.black.value, False, points, width=3)

        # screen_rect = self.touch_screen.base_surface.get_rect()
        # pg.draw.lines(self.touch_screen.base_surface, Colours.red.value, closed=False,
        #               points=[screen_rect.midtop, screen_rect.midbottom])
        # pg.draw.lines(self.touch_screen.base_surface, Colours.red.value, closed=False,
        #               points=[screen_rect.midleft, screen_rect.midright])
        self.target_coords = points

    def create_dataframe(self):
        return pd.DataFrame(data=self.spiral_data.transpose(),
                            columns=["pixel_x", "pixel_y", "rel_pos_x", "rel_pos_y", "theta", "error",
                                     "time"]), self.touch_size

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

        pixel_positions = [self.mouse_positions[idx, 0:2] - self.image_offset for idx in
                           range(len(self.mouse_positions))]
        rel_positions = [self.mouse_positions[idx, 0:2] - self.center_offset for idx in
                         range(len(self.mouse_positions))]
        errors = [(self.get_closest_coord_2(self.mouse_positions[idx, 0:2]))[2] for idx in
                  range(len(self.mouse_positions))]

        data = np.concatenate((np.array(pixel_positions), np.array(rel_positions),
                               np.expand_dims(self.mouse_positions[:, 3], axis=1),
                               np.expand_dims(np.array(errors), axis=1),
                               np.expand_dims(np.array(self.mouse_positions[:, 2] - self.mouse_positions[0, 2]),
                                              axis=1)), axis=1)

        self.output = pd.DataFrame(data=data,
                                   columns=["Plot X", "Plot Y", "rel_pos_x", "rel_pos_y", "theta", "error",
                                            "Time"]), self.touch_size

    def loop(self):
        self.entry_sequence()
        while self.running:
            for event in pg.event.get():
                if event.type == pg.MOUSEBUTTONDOWN:
                    if not self.spiral_started:
                        pos = self.get_relative_mose_pos()
                        idx, _, _ = self.get_closest_coord_2(np.array(pos))
                        self.mouse_positions = np.append(
                            self.mouse_positions, np.expand_dims([*pos, time.perf_counter(), idx], axis=0), axis=0)
                        self.spiral_started = True
                        self.prev_pos = pos - self.center_offset

                        if (pos - self.center_offset)[1] < 0:
                            self.turns -= 1

                    self.mouse_down = True

                elif event.type == pg.MOUSEMOTION and self.mouse_down:
                    pos = self.get_relative_mose_pos()
                    rel_pos = pos - self.center_offset

                    if rel_pos[0] > 0 and self.prev_pos[0] > 0 and self.prev_pos[1] >= 0 > rel_pos[1]:
                        self.turns -= 1  # anit-clockwise crossing of positive x-axis
                    elif rel_pos[0] > 0 and self.prev_pos[0] > self.prev_pos[1] <= 0 < rel_pos[1]:
                        self.turns += 1  # clockwise crossing of positive x-axis

                    if np.arctan2(*np.flip(pos - self.center_offset)) > 0:
                        angle = np.arctan2(*np.flip(pos - self.center_offset)) + 2 * np.pi * self.turns
                    else:
                        angle = np.arctan2(*np.flip(pos - self.center_offset)) + 2 * np.pi * (self.turns + 1)

                    print(angle)

                    idx, _, _ = self.get_closest_coord_2(np.array(pos))
                    self.mouse_positions = np.append(self.mouse_positions,
                                                     np.expand_dims([*pos, time.perf_counter(), angle], axis=0), axis=0)

                    if idx - self.coord_idx == 1:
                        pg.draw.line(self.touch_screen.base_surface, Colours.red.value,
                                     self.target_coords[self.coord_idx, :], self.target_coords[idx, :], width=3)
                        self.coord_idx += 1

                        if self.coord_idx == len(self.target_coords) - 1:
                            self.spiral_finished = True
                            self.running = False

                        self.update_display()

                    self.prev_pos = rel_pos

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
    os.chdir("/Users/benhoskings/Documents/Projects/hero-monitor")
    # os.chdir('/Users/Thinkpad/Desktop/Warwick/hero-monitor')
    # os.chdir("/Users/benhoskings/Documents/Pycharm/Hero_Monitor")

    pg.init()
    spiral_test = SpiralTest(turns=3)
    spiral_test.loop()  # optionally extract data from here as array
    spiral_data, spiral_size = spiral_test.output
    # Spiral data is a pd dataframe that contains the coordinates
    # reconstructed image should be of size spiral_size
    file_path=r'C:\Users\Thinkpad\Desktop\Warwick\hero-monitor\data\user_drawing\user_spiral.txt'
    spiral_data.to_csv(file_path, index=False)
    spiral_test.plot_data.to_csv("spiral_data_ref.csv", index=False)

    # reconstruct image
    spiral_image = pg.Surface(spiral_size, pg.SRCALPHA)  # create surface of correct size
    spiral_image.fill(Colours.white.value)  # fill with white background
    # draw in lines between each point recorded
    pg.draw.lines(spiral_image, Colours.black.value, False, spiral_data[["Plot X", "Plot Y"]].to_numpy(), width=3)

    img_array = pg.surfarray.array3d(spiral_image)  # extract the pixel data from the pygame surface
    img_array = cv2.transpose(img_array)  # transpose to switch from pg to cv2 axis
    img_array = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)  # switch from RGB (pygame) to BGR (cv2) colours
    cv2.imwrite("spiral.png", img_array)  # Save image
    os.chdir('/Users/Thinkpad/Desktop/Warwick/hero-monitor/data')

    data = FeatureEngineering()
    data.user_data()
    spiral = DataAnalytics()
    spiral.user_classify()
    spiral.error_graphs()
