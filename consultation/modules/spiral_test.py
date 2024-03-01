import numpy as np
import pygame as pg
import pandas as pd
import os
import time
import matplotlib.pyplot
import joblib

from consultation.touch_screen import TouchScreen, GameObjects
from consultation.screen import Colours
from consultation.display_screen import DisplayScreen
from consultation.spiral_data_analysis import DataAnalytics, FeatureEngineering

from consultation.utils import take_screenshot


def augment_data(input_data, spiral_radius):
    data_aug = input_data.assign(
        x_pos=(input_data["x_pos"] - spiral_radius) / spiral_radius,
        y_pos=(input_data["y_pos"] - spiral_radius) / spiral_radius
    )
    data_aug = data_aug.assign(
        time=(data_aug["time"] - data_aug.loc[0, "time"]) / 1000,
        magnitude=np.linalg.norm(data_aug[["x_pos", "y_pos"]], axis=1),
        theta=np.arctan2(data_aug["y_pos"], data_aug["x_pos"])
    )

    data_aug = data_aug.assign(
        distance=data_aug["magnitude"].diff(),
        angular_velocity=data_aug["theta"].diff() / data_aug["time"].diff()
    )
    turn_count = 0
    turns = np.array([])
    for row_idx in data_aug.index:
        if data_aug.loc[row_idx, "angular_velocity"] > np.pi * 2:
            turn_count += 1

        turns = np.append(turns, turn_count)

    data_aug = data_aug.assign(
        turns=turns,
        theta=data_aug["theta"] + turns * 2 * np.pi
    )

    data_aug = data_aug.assign(
        angular_velocity=data_aug["theta"].diff() / data_aug["time"].diff()
    )
    return data_aug


def create_feature(spiral_data):
    spiral_data: pd.DataFrame
    mean_values = np.mean(spiral_data, axis=0)
    sum_values = np.sum(spiral_data, axis=0)
    rms_vals = np.sqrt(np.mean(spiral_data ** 2, axis=0))

    return np.array(np.concatenate([mean_values.values, sum_values.values, rms_vals.values]))


class SpiralTest:
    def __init__(self, turns, size=(1024, 600), spiral_size=400, parent=None, draw_trace=False, auto_run=False):
        self.parent = None
        if parent is not None:
            self.display_size = parent.display_size
            self.bottom_screen = parent.bottom_screen
            self.top_screen = parent.top_screen

            self.display_screen = DisplayScreen(self.display_size, avatar=parent.avatar)

        else:
            self.display_size = pg.Vector2(size)
            self.window = pg.display.set_mode((self.display_size.x, self.display_size.y * 2), pg.SRCALPHA)

            self.top_screen = self.window.subsurface(((0, 0), self.display_size))
            self.bottom_screen = self.window.subsurface((0, self.display_size.y), self.display_size)
            self.display_screen = DisplayScreen(self.display_size)

        self.display_screen.instruction = "Start in the center"

        self.spiral_size = pg.Vector2(spiral_size, spiral_size)
        self.touch_screen = TouchScreen(size, colour=Colours.white)

        self.target_coords = None
        self.theta_vals = None

        self.plot_data = None
        self.turns = turns
        self.spiral_offset = (self.display_size - self.spiral_size) / 2
        self.center_offset = self.display_size / 2
        self.load_surface(size=self.spiral_size, turns=turns)

        self.coord_idx = 0

        self.mouse_down = False

        self.running = True

        self.tracking_data = pd.DataFrame(data=None, columns=["x_pos", "y_pos", "time"])
        self.start_time = None
        self.spiral_started = False
        self.spiral_finished = False
        self.prev_pos = None
        self.turns = 0

        self.prediction_model = joblib.load("data/linear_regression_model.joblib")

        self.output = None
        self.draw_trace = draw_trace
        self.auto_run = auto_run

    def update_display(self):
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
        theta = np.sqrt(np.linspace(0, (2 * np.pi) ** 2, n))  # Spiral parametrised by theta
        self.theta_vals = theta * turns
        x = (b * theta) * np.cos(turns * theta)  # x component of coordinate
        y = (b * theta) * np.sin(turns * theta)  # y component of coordinate
        points = np.array(([x + 0.5, y + 0.5])).transpose()  # spiral coordinates: Nx2 np array (N is number of points)

        # Scale to the size of the surface
        points = np.array([points[:, 0] * size[0], (points[:, 1]) * size[1]]).transpose()  # Scale to size of surface

        # Apply additional options
        # if not clockwise:
        #     points[:, 1] = (size[1] - points[:, 1])

        center_points = points - pg.Vector2(size) / 2

        plot_data = np.concatenate([
            np.expand_dims(center_points[:, 0], axis=1), np.expand_dims(center_points[:, 1], axis=1),
            np.expand_dims(theta * turns, axis=1),
            np.expand_dims(np.linalg.norm(np.concatenate([np.expand_dims(center_points[:, 0], axis=1),
                                                          np.expand_dims(center_points[:, 1], axis=1)], axis=1),
                                          axis=1), axis=1)], axis=1)

        self.plot_data = pd.DataFrame(plot_data, columns=["x", "y", "theta", "mag"])

        points += np.array([self.spiral_offset.x, self.spiral_offset.y])

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
                                     "time"]), self.spiral_size

    def entry_sequence(self):
        self.update_display()
        if self.parent:
            self.parent.speak_text("Please trace the spiral, starting from the center", visual=False)

    def exit_sequence(self):
        self.update_display()
        if self.parent:
            self.parent.speak_text("Thank you for completing the spiral test", visual=False)

        data_aug = augment_data(self.tracking_data, spiral_radius=self.spiral_size.x/2)
        print(data_aug.columns)
        spiral_features = create_feature(data_aug)

        prediction = self.prediction_model.predict(spiral_features.reshape(1, -1))
        print(prediction)

        # pixel_positions = [self.mouse_positions[idx, 0:2] - self.spiral_offset for idx in
        #                    range(len(self.mouse_positions))]
        # rel_positions = [self.mouse_positions[idx, 0:2] - self.center_offset for idx in
        #                  range(len(self.mouse_positions))]
        # errors = [(self.get_closest_coord_2(self.mouse_positions[idx, 0:2]))[2] for idx in
        #           range(len(self.mouse_positions))]
        #
        # data = np.concatenate((np.array(pixel_positions), np.array(rel_positions),
        #                        np.expand_dims(self.mouse_positions[:, 3], axis=1),
        #                        np.expand_dims(np.array(errors), axis=1),
        #                        np.expand_dims(np.array(self.mouse_positions[:, 2] - self.mouse_positions[0, 2]),
        #                                       axis=1)), axis=1)
        #
        # self.output = pd.DataFrame(data=data,
        #                            columns=["Plot X", "Plot Y", "rel_pos_x", "rel_pos_y", "theta", "error",
        #                                     "Time"]), self.spiral_size

        # selected_data = self.tracking_data.columns
        # print(selected_data)

    def process_input(self, pos):
        rel_pos = pos - self.center_offset
        true_pos = [self.center_offset[0] + rel_pos[0], self.center_offset[1] - rel_pos[1]]

        if rel_pos[0] > 0 and self.prev_pos[0] > 0 and self.prev_pos[1] >= 0 > rel_pos[1]:
            self.turns -= 1  # anit-clockwise crossing of positive x-axis
        elif rel_pos[0] > 0 and self.prev_pos[0] > self.prev_pos[1] <= 0 < rel_pos[1]:
            self.turns += 1  # clockwise crossing of positive x-axis
            # print(self.turns)

        if np.arctan2(*np.flip(pos - self.center_offset)) > 0:
            angle = np.arctan2(*np.flip(pos - self.center_offset)) + 2 * np.pi * self.turns
        else:
            angle = np.arctan2(*np.flip(pos - self.center_offset)) + 2 * np.pi * (self.turns + 1)

        idx, _, _ = self.get_closest_coord_2(np.array(pos))
        self.tracking_data.loc[self.tracking_data.shape[0]] = [*(pos - self.spiral_offset), time.monotonic() - self.start_time]

        update_flag = False
        if self.draw_trace:
            # PLOT BLUE LINE HERE
            pg.draw.line(self.touch_screen.base_surface, Colours.blue.value,
                         self.prev_pos+self.center_offset, pos, width=3)
            update_flag = True

        if idx - self.coord_idx < 10:
            for i in range(idx - self.coord_idx):
                pg.draw.line(self.touch_screen.base_surface, Colours.red.value,
                             self.target_coords[self.coord_idx, :],
                             self.target_coords[min([idx, self.target_coords.shape[0]-1]), :], width=3)

                self.coord_idx += 1
                idx += 1

            if self.coord_idx == len(self.target_coords) - 1:
                self.spiral_finished = True
                self.running = False

            update_flag = True

        if update_flag:
            self.update_display()

    def loop(self):
        self.entry_sequence()
        while self.running:
            if self.auto_run:
                self.start_time = time.monotonic()

                mu, sigma = 0.01, 0.001
                sim_positions = self.target_coords + np.random.normal(0, 4, self.target_coords.shape)
                start_pos = sim_positions[0, :]

                self.tracking_data.loc[self.tracking_data.shape[0]] = [*(start_pos - self.spiral_offset), time.monotonic() - self.start_time]
                self.prev_pos = pg.Vector2(start_pos.tolist()) - self.center_offset

                for idx in range(1, sim_positions.shape[0]):
                    pos = pg.Vector2(sim_positions[idx, :].tolist())

                    self.process_input(pos)
                    self.prev_pos = pos - self.center_offset

                    if idx == 100:

                        take_screenshot(self.window, "spiral_test")

                print(self.tracking_data["time"].shape, np.cumsum(sigma * np.random.randn(sim_positions.shape[0]) + mu).shape)

                self.tracking_data.loc[:, "time"] = np.cumsum(sigma * np.random.randn(sim_positions.shape[0]) + mu)

                # self.auto_run = False
                self.running = False
            else:
                for event in pg.event.get():
                    if event.type == pg.MOUSEBUTTONDOWN:
                        if not self.spiral_started:
                            pos = pg.Vector2(pg.mouse.get_pos()) - pg.Vector2(0, self.display_size.y)
                            idx, _, _ = self.get_closest_coord_2(np.array(pos))
                            self.mouse_positions = np.append(
                                self.mouse_positions, np.expand_dims([*pos, time.perf_counter(), idx], axis=0), axis=0)
                            self.spiral_started = True
                            self.prev_pos = pos - self.center_offset

                            if (pos - self.center_offset)[1] < 0:
                                self.turns -= 1

                        self.mouse_down = True

                    elif event.type == pg.MOUSEMOTION and self.mouse_down:
                        pos = pg.Vector2(pg.mouse.get_pos()) - pg.Vector2(0, self.display_size.y)
                        print(pos)
                        self.process_input(pos)

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
    pg.event.pump()

    spiral_test = SpiralTest(turns=3, draw_trace=True, auto_run=True, spiral_size=600)
    spiral_test.loop()  # optionally extract data from here as array
    spiral_data, spiral_size = spiral_test.output
    # Spiral data is a pd dataframe that contains the coordinates
    # reconstructed image should be of size spiral_size
    # file_path = r'\user_drawing\user_spiral.txt'
    # spiral_data.to_csv(file_path, index=False)
    # spiral_test.plot_data.to_csv("spiral_data_ref.csv", index=False)
    #
    # # reconstruct image
    # spiral_image = pg.Surface(spiral_size, pg.SRCALPHA)  # create surface of correct size
    # spiral_image.fill(Colours.white.value)  # fill with white background
    # # draw in lines between each point recorded
    # pg.draw.lines(spiral_image, Colours.black.value, False, spiral_data[["Plot X", "Plot Y"]].to_numpy(), width=3)
    #
    # img_array = pg.surfarray.array3d(spiral_image)  # extract the pixel data from the pygame surface
    # img_array = cv2.transpose(img_array)  # transpose to switch from pg to cv2 axis
    # img_array = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)  # switch from RGB (pygame) to BGR (cv2) colours
    # cv2.imwrite("spiral.png", img_array)  # Save image

    # os.chdir(os.getcwd() + "/data")
    #
    # feature_engineering = FeatureEngineering(spiral_data)
    # spiral_data_aug = feature_engineering.process_data()
    #
    # spiral_analytics = DataAnalytics(spiral_data=spiral_data_aug)
    # spiral_analytics.classify()

    # spiral.get_prob_reg(spiral_data_aug, 'user_data')
    # spiral.error_graphs()
