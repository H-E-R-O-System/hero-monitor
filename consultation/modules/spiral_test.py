import numpy as np
import pygame as pg
import pandas as pd
import os
import time
import matplotlib.pyplot as plt
import joblib

from consultation.touch_screen import TouchScreen, GameObjects
from consultation.screen import Colours, BlitLocation
from consultation.display_screen import DisplayScreen

from consultation.utils import take_screenshot, Buttons, ButtonModule


def augment_data(input_data, spiral_radius, invert_y=False, time_unit="seconds"):
    if invert_y:
        data_aug = input_data.assign(
            x_pos=(input_data["x_pos"] - spiral_radius) / spiral_radius,
            y_pos=(spiral_radius - input_data["y_pos"]) / spiral_radius
        )
    else:
        data_aug = input_data.assign(
            x_pos=(input_data["x_pos"] - spiral_radius) / spiral_radius,
            y_pos=(input_data["y_pos"] - spiral_radius) / spiral_radius
        )

    if not time_unit == "seconds":
        data_aug = data_aug.assign(time=(data_aug["time"] - min(data_aug["time"])) / 1000)

    data_aug = data_aug.assign(magnitude=np.linalg.norm(data_aug[["x_pos", "y_pos"]], axis=1))

    data_aug = data_aug.assign(distance=data_aug["magnitude"].diff())

    turn_count = 0
    if data_aug.loc[0, "y_pos"] < 0:
        turn_count -= 1

    turns = np.array([turn_count])
    angles = np.array([])
    for row_idx in data_aug.index:
        pos = data_aug.loc[row_idx, ["x_pos", "y_pos"]].values
        if row_idx > 0:
            prev_pos = data_aug.loc[row_idx - 1, ["x_pos", "y_pos"]].values
            if pos[0] > 0 and prev_pos[0] > 0 and prev_pos[1] >= 0 > pos[1]:
                turn_count -= 1  # anit-clockwise crossing of positive x-axis
            elif pos[0] > 0 and prev_pos[0] > prev_pos[1] <= 0 < pos[1]:
                turn_count += 1  # clockwise crossing of positive x-axis
            turns = np.append(turns, turn_count)

        atan_result = np.arctan2(pos[1], pos[0])

        if pos[1] == pos[0] == 0:
            angle = 0
        elif atan_result > 0:
            angle = atan_result + 2 * np.pi * turn_count
        else:
            angle = atan_result + 2 * np.pi * (turn_count + 1)

        angles = np.append(angles, angle)

    data_aug = data_aug.assign(
        turns=turns,
        theta=angles
    )
    # print(((data_aug["theta"] / 2 * np.pi * 3) - data_aug["magnitude"]))
    data_aug = data_aug.assign(
        error=((data_aug["theta"] / (2 * np.pi * 3)) - data_aug["magnitude"]) * data_aug["theta"],
        angular_velocity=data_aug["theta"].diff() / data_aug["time"].diff()
    )

    return data_aug[['x_pos', 'y_pos', 'time', 'magnitude', 'distance', 'turns', 'theta', 'angular_velocity', "error"]]


def create_feature(spiral_data):
    return np.mean(spiral_data, axis=0)


class SpiralTest:
    def __init__(self, turns, size=(1024, 600), spiral_size=400, parent=None, draw_trace=False, auto_run=False):
        self.parent = parent
        if parent is not None:
            self.display_size = parent.display_size
            self.bottom_screen = parent.bottom_screen
            self.top_screen = parent.top_screen

            self.display_screen = DisplayScreen(self.display_size, avatar=parent.avatar)
            self.button_module = parent.button_module

        else:
            self.display_size = pg.Vector2(size)
            self.window = pg.display.set_mode((self.display_size.x, self.display_size.y * 2), pg.SRCALPHA)

            self.top_screen = self.window.subsurface(((0, 0), self.display_size))
            self.bottom_screen = self.window.subsurface((0, self.display_size.y), self.display_size)
            self.display_screen = DisplayScreen(self.display_size)
            self.button_module = ButtonModule(pi=False)

        self.display_screen.instruction = "Start in the center."

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

        self.prediction_model = joblib.load("models/linear_regression_model.joblib")

        self.prediction, self.classification = None, None
        self.draw_trace = draw_trace
        self.auto_run = auto_run
        self.show_info = False
        self.power_off = False

    def update_display(self, top=True):
        if top:
            self.top_screen.blit(self.display_screen.get_surface(), (0, 0))
            self.bottom_screen.blit(self.touch_screen.get_surface(), (0, 0))
        else:
            self.bottom_screen.blit(self.touch_screen.base_surface, (0, 0))
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

        pg.draw.lines(self.touch_screen.base_surface, Colours.black.value, False, points, width=5)

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
            print("speaking")
            self.parent.speak_text("Please trace the spiral, starting from the center",
                                   display_screen=self.display_screen, touch_screen=self.touch_screen)

            if self.parent.pi:
                pg.mouse.set_cursor(pg.cursors.Cursor(pg.SYSTEM_CURSOR_CROSSHAIR))
                pg.mouse.set_visible(True)

    def exit_sequence(self):
        self.update_display()
        if self.parent:
            self.parent.speak_text("Thank you for completing the spiral test", display_screen=self.display_screen,
                                   touch_screen=self.touch_screen)

        data_aug = augment_data(self.tracking_data, spiral_radius=self.spiral_size.x / 2)
        # print(data_aug.tail(20).to_string())
        # plt.scatter(data_aug["x_pos"], data_aug["y_pos"])
        # plt.show()
        #
        # plt.plot(data_aug["time"], data_aug["theta"])
        # plt.show()
        spiral_features = create_feature(data_aug)

        prediction = self.prediction_model.predict(spiral_features.values.reshape(1, -1))
        self.prediction = prediction[0]
        self.classification = self.prediction > 0.5

        if self.parent:
            if self.parent.pi:
                pg.mouse.set_visible(False)

    def process_input(self, pos):
        start = time.monotonic()
        idx, _, _ = self.get_closest_coord_2(np.array(pos))
        self.tracking_data.loc[self.tracking_data.shape[0]] = [*(pos - self.spiral_offset),
                                                               time.monotonic() - self.start_time]

        update_flag = False
        if self.draw_trace:
            # PLOT BLUE LINE HERE
            pg.draw.line(self.touch_screen.base_surface, Colours.blue.value,
                         self.prev_pos + self.center_offset, pos, width=3)
            update_flag = True

        if idx - self.coord_idx < 10:
            if (idx - self.coord_idx) > 0:
                for i in range(self.coord_idx, idx + 1):
                    pg.draw.line(self.touch_screen.base_surface, Colours.red.value,
                                 self.target_coords[i, :],
                                 self.target_coords[min(self.target_coords.shape[0] - 1, i + 1), :], width=5)

                self.coord_idx = idx

                if self.coord_idx == len(self.target_coords) - 1:
                    self.spiral_finished = True
                    self.running = False

                update_flag = True

        if update_flag:
            self.update_display(top=False)

        # print(f"process time: {time.monotonic() - start}")

    def button_actions(self, selected):

        if selected == Buttons.info and not self.power_off:
            self.show_info = not self.show_info
            self.toggle_info_screen()
        elif selected == Buttons.power:
            self.power_off = not self.power_off

            self.display_screen.power_off = self.power_off
            self.touch_screen.power_off = self.power_off

            if self.power_off:
                self.display_screen.instruction = None

                self.update_display(top=True)
            else:
                self.touch_screen.refresh()
                self.toggle_info_screen()

        else:
            ...
            print("Power")

    def toggle_info_screen(self):
        if self.show_info:
            self.display_screen.state = 1
            self.display_screen.instruction = None

            info_rect = pg.Rect(0.3 * self.display_size.x, 0, 0.7 * self.display_size.x, 0.8 * self.display_size.y)
            pg.draw.rect(self.display_screen.surface, Colours.white.value,
                         info_rect)

            self.display_screen.add_multiline_text("Trace the spiral!", rect=info_rect.scale_by(0.9, 0.9),
                                                   font_size=50)
            # info_text = ("In this game you must select the bottom card that you think matches the top card "
            #              "You must work out how to match the cards from me telling you if you are correct or not. "
            #              "The way in which cards match will change throughout the game, so you must adapt for this too! "
            #              "An example of a match is shown below.")

            info_text = (
                "In this game you must trace the spiral using the pen provided. Make sure that the red line follows "
                "your pen as you trace the spiral!")

            self.display_screen.add_multiline_text(
                rect=info_rect.scale_by(0.9, 0.9), text=info_text,
                center_vertical=True, font_size=40)

            self.update_display(top=True)
        else:
            self.display_screen.refresh()
            self.display_screen.state = 0
            self.display_screen.instruction = "Start in the center."
            self.update_display(top=True)

    def loop(self):
        self.entry_sequence()
        while self.running:
            if self.auto_run:

                def moving_average(x, w):
                    return np.convolve(x, np.ones(w), 'same') / w

                moving_error_x = moving_average(np.cumsum(np.random.normal(0, 0.8, self.target_coords.shape[0])), 5)
                moving_error_y = moving_average(np.cumsum(np.random.normal(0, 0.8, self.target_coords.shape[0])), 5)
                mu, sigma = 0.05, 0.001
                sim_positions = self.target_coords + np.concatenate(
                    [moving_error_x.reshape(-1, 1), moving_error_y.reshape(-1, 1)], axis=1)
                start_pos = sim_positions[0, :]

                self.tracking_data.loc[self.tracking_data.shape[0]] = [
                    *(start_pos - self.spiral_offset), 0
                ]
                self.prev_pos = pg.Vector2(start_pos.tolist()) - self.center_offset

                self.start_time = time.monotonic()

                for idx in range(1, sim_positions.shape[0]):
                    pos = pg.Vector2(sim_positions[idx, :].tolist())

                    self.process_input(pos)
                    self.prev_pos = pos - self.center_offset

                    # if idx == 100:
                    #     take_screenshot(self.window, "spiral_test")

                self.tracking_data.loc[:, "time"] = np.cumsum(sigma * np.random.randn(sim_positions.shape[0]) + mu)

                # self.auto_run = False
                self.running = False
            else:
                for event in pg.event.get():
                    if event.type == pg.MOUSEBUTTONDOWN and not self.power_off:
                        if not self.spiral_started:
                            pos = pg.Vector2(pg.mouse.get_pos()) - pg.Vector2(0, self.display_size.y)

                            self.tracking_data.loc[self.tracking_data.shape[0]] = [
                                *(pos - self.spiral_offset), 0
                            ]

                            self.prev_pos = pos - self.center_offset
                            self.spiral_started = True
                            self.start_time = time.monotonic()

                        self.mouse_down = True

                    elif event.type == pg.MOUSEMOTION and self.mouse_down and not self.power_off:
                        pos = pg.Vector2(pg.mouse.get_pos()) - pg.Vector2(0, self.display_size.y)
                        self.process_input(pos)
                        self.prev_pos = pos - self.center_offset

                    elif event.type == pg.MOUSEBUTTONUP and not self.power_off:
                        self.mouse_down = False

                    elif event.type == pg.KEYDOWN and not self.power_off:
                        if event.key == pg.K_s:
                            if self.parent:
                                take_screenshot(self.parent.window)
                            else:
                                take_screenshot(self.window, "Spiral trace")

                    elif event.type == pg.QUIT:
                        self.running = False

                selected = self.button_module.check_pressed()
                if selected is not None:
                    self.button_actions(selected)

        self.exit_sequence()


if __name__ == "__main__":
    os.chdir("../..")

    pg.init()
    pg.event.pump()

    spiral_test = SpiralTest(turns=3, draw_trace=True, auto_run=False, spiral_size=600)

    spiral_test.loop()  # optionally extract data from here as array
    print(spiral_test.classification, spiral_test.prediction)
    # print(spiral_test.tracking_data)
