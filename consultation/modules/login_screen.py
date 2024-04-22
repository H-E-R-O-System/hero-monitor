import time

import pygame as pg
from consultation.utils import Buttons, ButtonModule, take_screenshot
from consultation.screen import Screen, Fonts, Colours
from consultation.display_screen import DisplayScreen
from consultation.touch_screen import TouchScreen, GameObjects, GameButton
import math
import os
import pandas as pd


class User:
    def __init__(self, name, age, id):
        self.id = id
        self.name = name
        self.age = age


class LoginScreen:
    def __init__(self, size=(1024, 600), parent=None, username=None, password=None, auto_run=False):
        self.parent = parent
        if parent is not None:
            self.display_size = parent.display_size
            self.bottom_screen = parent.bottom_screen
            self.top_screen = parent.top_screen
            self.all_user_data = parent.all_user_data
            self.display_screen = DisplayScreen(self.display_size, avatar=parent.avatar)
            self.button_module = parent.button_module

        else:
            self.display_size = pg.Vector2(size)
            self.window = pg.display.set_mode((self.display_size.x, self.display_size.y * 2), pg.SRCALPHA)

            self.top_screen = self.window.subsurface(((0, 0), self.display_size))
            self.bottom_screen = self.window.subsurface((0, self.display_size.y), self.display_size)
            self.display_screen = DisplayScreen(self.display_size)

            if os.path.exists("data/user_data.csv"):
                self.all_user_data = pd.read_csv("data/user_data.csv")
                self.all_user_data = self.all_user_data.set_index("Username")
            else:
                self.all_user_data = None

            self.button_module = ButtonModule(pi=False)

        self.info_rect = pg.Rect(0.3 * self.display_size.x, 0, 0.7 * self.display_size.x, 0.8 * self.display_size.y)
        pg.draw.rect(self.display_screen.base_surface, Colours.white.value, self.info_rect)

        self.display_screen.state = 1
        # self.display_screen.add_multiline_text("Please enter your login details",
        #                                        rect=self.info_rect.scale_by(0.9, 0.9),
        #                                        font_size=40, base=True)

        self.touch_screen = TouchScreen(self.display_size)

        top_size = pg.Vector2(self.display_size.x * 0.4, 80)
        username_button = GameButton(
            position=pg.Vector2(0.25 * self.display_size.x, 0.1 * self.display_size.y) - top_size / 2,
            size=top_size, id="username", text="enter username")
        password_button = GameButton(
            position=pg.Vector2(0.75 * self.display_size.x, 0.1 * self.display_size.y) - top_size / 2,
            size=top_size, id="password", text="enter password")
        delete_size = pg.Vector2(160, 80)
        delete_button = GameButton(
            position=pg.Vector2(0.9 * self.display_size.x - delete_size.x / 2, 0.65 * self.display_size.y),
            size=delete_size, id="delete", text="delete")
        enter_button = GameButton(
            position=pg.Vector2(0.9 * self.display_size.x - delete_size.x / 2, 0.82 * self.display_size.y),
            size=delete_size, id="enter", text="submit")

        # Additional class properties
        letters_1 = ["q", "w", "e", "r", "t", "y", "u", "i", "o", "p"]
        letters_2 = ["a", "s", "d", "f", "g", "h", "j", "k", "l"]
        letters_3 = ["z", "x", "c", "v", "b", "n", "m"]

        size = pg.Vector2(80, 80)

        option_count = 10
        card_width, h_gap = math.pow(option_count + 1, -1), math.pow(option_count + 1, -2)

        line_1 = [((idx * card_width + (idx + 2) * h_gap) * self.display_size.x,
                   0.24 * self.display_size.y) for idx in range(10)]
        line_2 = [(((idx + 0.3) * card_width + (idx + 2) * h_gap) * self.display_size.x,
                   0.44 * self.display_size.y) for idx in range(9)]
        line_3 = [(((idx + 0.8) * card_width + (idx + 2) * h_gap) * self.display_size.x,
                   0.64 * self.display_size.y) for idx in range(7)]

        # print(self.option_coords)

        space_size = pg.Vector2(500, 80)
        space_rect = pg.Rect(pg.Vector2(0.42 * self.display_size.x - space_size.x / 2, 0.82 * self.display_size.y),
                             space_size)
        self.keys = ([GameButton(position=line_1[idx], size=size, id=letters_1[idx], text=letters_1[idx])
                      for idx in range(10)] +
                     [GameButton(position=line_2[idx], size=size, id=letters_2[idx], text=letters_2[idx])
                      for idx in range(9)] +
                     [GameButton(position=line_3[idx], size=size, id=letters_3[idx], text=letters_3[idx])
                      for idx in range(7)] +
                     [GameButton(position=space_rect.topleft, size=space_rect.size, id=" "),
                      delete_button, enter_button, password_button, username_button, ])

        self.active_string = "user"
        self.user = None
        self.keys[-2].colour = Colours.lightGrey.value  # grey out password
        self.running = False

        if username and password:
            self.user_string = list(username)
            self.pass_string = list(password)
        else:
            self.user_string = []
            self.pass_string = []

        self.auto_run = auto_run

        self.power_off = False

    def update_display(self):
        self.display_screen.refresh()

        user_rect = self.info_rect.scale_by(0.9, 0.8)
        user_rect = pg.Rect(user_rect.topleft+ pg.Vector2(0, 50), (user_rect.w, 80))
        pass_rect = pg.Rect(user_rect.topleft + pg.Vector2(0, 150), user_rect.size)
        # pg.draw.rect(self.display_screen.surface, color=Colours.hero_blue.value, rect=user_rect)
        if self.active_string == "user":
            user_text = Colours.white
            user_bg = Colours.hero_blue
            pass_text = Colours.hero_blue
            pass_bg = Colours.white
        else:
            user_text = Colours.hero_blue
            user_bg = Colours.white
            pass_text = Colours.white
            pass_bg = Colours.hero_blue

        self.display_screen.add_multiline_text(
            rect=user_rect, text=f'Username: {"".join(self.user_string)}',
            center_vertical=True, font_size=60, colour=user_text, bg_colour=user_bg,
            border_width=10)
        self.display_screen.add_multiline_text(
            rect=pass_rect, text=f'Password: {"".join(["*" for _ in self.pass_string])}',
            center_vertical=True, font_size=60, colour=pass_text, bg_colour=pass_bg,
            border_width=10)

        self.top_screen.blit(self.display_screen.get_surface(), (0, 0))
        self.bottom_screen.blit(self.touch_screen.get_surface(), (0, 0))
        pg.display.flip()

        # print(self.display_screen.instruction)

    def check_credentials(self):
        username, password = "".join(self.user_string), "".join(self.pass_string)

        if self.all_user_data is not None:
            if username in self.all_user_data.index:
                # print("user recognised")
                if self.all_user_data.loc[username, "Password"] == password:
                    return True

        return False

    def entry_sequence(self):
        # pre-loop initialisation section
        # add everything needed to introduce your module and explain
        # what the users are expected to do (e.g. game rules, aim, etc.)

        self.running = True
        self.update_display()  # render graphics to main consult

        if self.parent:
            self.parent.speak_text("Welcome to the HERO consultation",
                                   visual=True, display_screen=self.display_screen, touch_screen=self.touch_screen)
            self.parent.speak_text("Please enter your login details to continue",
                                   visual=True, display_screen=self.display_screen, touch_screen=self.touch_screen)

        self.display_screen.instruction = "Please enter your details"
        self.touch_screen.sprites = GameObjects(self.keys)
        self.update_display()
        # add code below

        if self.user_string and self.pass_string and self.auto_run:
            if self.check_credentials():
                self.running = False

    def exit_sequence(self):
        # post-loop completion section
        # maybe add short thank you for completing the section?

        # only OPTIONAL and can leave blank
        self.running = False
        username, password = "".join(self.user_string), "".join(self.pass_string)
        user_data = self.all_user_data.loc[username]
        return User(name=user_data["FirstName"], age=21, id=user_data["UserID"])

    def loop(self):
        self.entry_sequence()
        while self.running:
            for event in pg.event.get():
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_s:
                        # do something with key press
                        if self.parent:
                            take_screenshot(self.parent.window)
                        else:
                            take_screenshot(self.window, "login_screen")

                    elif event.key == pg.K_ESCAPE:
                        self.running = False

                elif event.type == pg.MOUSEBUTTONDOWN:
                    # do something with mouse click
                    mouse_pos = pg.Vector2(pg.mouse.get_pos()) - pg.Vector2(0, self.display_size.y)
                    button_id = self.touch_screen.click_test(mouse_pos)
                    if button_id is not None:
                        if button_id == "username":
                            self.active_string = "user"
                            self.keys[-1].colour = Colours.hero_blue.value  # grey out password
                            self.keys[-2].colour = Colours.lightGrey.value
                        elif button_id == "password":
                            self.active_string = "pass"
                            self.keys[-1].colour = Colours.lightGrey.value  # grey out password
                            self.keys[-2].colour = Colours.hero_blue.value

                        else:
                            button = self.touch_screen.get_object(button_id)
                            button.colour = Colours.lightGrey.value
                            self.update_display()

                            if button_id == "delete":
                                if self.active_string == "user" and self.user_string:
                                    del self.user_string[-1]
                                elif self.active_string == "pass" and self.pass_string:
                                    del self.pass_string[-1]
                            elif button_id == "enter":
                                if not self.pass_string:
                                    self.active_string = "pass"
                                    self.active_string = "pass"
                                    self.keys[-1].colour = Colours.lightGrey.value  # grey out password
                                    self.keys[-2].colour = Colours.hero_blue.value
                                elif self.check_credentials():
                                    self.running = False
                                else:
                                    if self.parent:
                                        self.parent.speak_text(
                                            "I dont recognise that user, please check your details again",
                                            visual=True, display_screen=self.display_screen, touch_screen=self.touch_screen)

                                    self.pass_string = []
                            else:
                                if self.active_string == "user":
                                    self.user_string.append(button_id)
                                elif self.active_string == "pass":
                                    self.pass_string.append(button_id)

                            time.sleep(0.1)
                            button.colour = Colours.hero_blue.value

                        self.update_display()

                elif event.type == pg.QUIT:
                    # break the running loop
                    self.running = False

            selected = self.button_module.check_pressed()
            if selected is not None:
                self.button_actions(selected)

        output = self.exit_sequence()
        return output


if __name__ == "__main__":

    os.chdir("/Users/benhoskings/Documents/Pycharm/Hero_Monitor")
    pg.init()
    # Module Testing
    login_screen = LoginScreen()
    login_screen.loop()
    print("Module run successfully")
