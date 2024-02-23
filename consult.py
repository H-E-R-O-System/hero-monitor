# import packages
import datetime
import os.path

import cv2
import gtts
import os
import string
import shutil
import time
import re
from datetime import date

import numpy as np
import pandas as pd
import pygame as pg

from consultation.avatar import Avatar
from consultation.display_screen import DisplayScreen
# import consultation modules
from consultation.modules.perceived_stress_score import PSS
from consultation.modules.spiral_test import SpiralTest
from consultation.modules.wisconsin_card_test import CardGame
from consultation.modules.visual_attention_test import VisualAttentionTest
from consultation.modules.shape_searcher import ShapeSearcher
from consultation.modules.clock_draw import ClockDraw
from consultation.modules.keyboard import LoginScreen

# import graphics helpers
from consultation.screen import Colours, Fonts
from consultation.touch_screen import TouchScreen, GameObjects, GameButton


class User:
    def __init__(self, name, age, id):
        self.id = id
        self.name = name
        self.age = age


class ConsultConfig:
    def __init__(self, speech=True):
        self.speech = speech
        self.text = True
        self.output_lang = 'en'
        self.input_lang = 'en'


class Consultation:
    def __init__(self, user=None, enable_speech=True, scale=1, pi=True):

        if user:
            self.user = user
        else:
            # create demo user
            self.user = User("Demo", 65, 0)

        self.config = ConsultConfig(speech=enable_speech)
        if not os.path.isdir("consultation/question_audio_tmp"):
            os.mkdir("consultation/question_audio_tmp")

        self.display_size = pg.Vector2(1024, 600) * scale

        # load all attributes which utilise any pygame surfaces!

        if pi:
            self.window = pg.display.set_mode((self.display_size.x, self.display_size.y * 2), pg.NOFRAME | pg.SRCALPHA)
        else:
            self.window = pg.display.set_mode((self.display_size.x, self.display_size.y * 2), pg.SRCALPHA)

        self.top_screen = self.window.subsurface(((0, 0), self.display_size))
        self.bottom_screen = self.window.subsurface((0, self.display_size.y), self.display_size)

        self.fonts = Fonts()
        self.display_screen = DisplayScreen(self.top_screen.get_size())
        self.display_screen.instruction = "Click the button to start"
        self.touch_screen = TouchScreen(self.bottom_screen.get_size())
        button_size = pg.Vector2(300, 200)
        self.quit_button = GameButton((10, 10), pg.Vector2(70, 50), id=2, text="QUIT", colour=Colours.red)
        self.main_button = GameButton((self.display_size - button_size) /2, button_size, id=1, text="Start")
        self.touch_screen.sprites = GameObjects([self.quit_button, self.main_button])

        self.avatar = Avatar(size=(self.display_size.y * 0.7, self.display_size.y * 0.7))
        # self.avatar = Avatar(scale=pg.Vector2(3, 3))
        self.display_screen.avatar = self.avatar

        self.pss_question_count = 2
        self.modules = {
            "Shapes": ShapeSearcher(max_turns=10, parent=self),
            "Spiral": SpiralTest(turns=3, touch_size=(self.display_size.y*0.9, self.display_size.y*0.9), parent=self),
            "VAT": VisualAttentionTest(touch_size=(self.display_size.y*0.9, self.display_size.y*0.9), parent=self),
            "WCT": CardGame(max_turns=8, parent=self),
            "PSS": PSS(self, question_count=self.pss_question_count),
            "Clock": ClockDraw(parent=self),
            "Login": LoginScreen(parent=self)
        }

        self.module_order = ["Login", "WCT", "Shapes", "PSS", "Spiral", "VAT",]

        self.module_idx = 0

        self.output = None

        self.running = True

        self.id = self.generate_unique_id()

        self.update_display()

    def generate_unique_id(self):
        letters = pd.Series(list(string.ascii_lowercase))[np.random.permutation(26)][:10].values
        numbers = np.random.permutation(10)[:5]
        num_pos = np.sort(np.random.permutation(15)[:5])
        for idx, num in zip(num_pos, numbers):
            letters = np.insert(letters, idx, num)

        id = ""
        for elem in letters:
            id = f"{id}{elem}"

        return id

    def update_display(self, display_screen=None, touch_screen=None):
        if display_screen is None:
            display_screen = self.display_screen
        if touch_screen is None:
            touch_screen = self.touch_screen

        # touch_screen.refresh()
        # display_screen.refresh()

        self.top_screen.blit(display_screen.get_surface(), (0, 0))
        self.bottom_screen.blit(touch_screen.get_surface(), (0, 0))
        pg.display.flip()

    def speak_text(self, text, visual=True, display_screen=None, touch_screen=None):

        if not display_screen:
            display_screen = self.display_screen

        if not touch_screen:
            touch_screen = self.touch_screen

        text_index = text.lower()

        text_index = text_index.replace(" ", "0 ").replace(".", "0 ").replace(",", "0 ")
        rep_1 = {"th": "11 ", "sh": "9 ", "ch": "9 ", "ee": "3 "}
        rep_2 = {"a": "1 ", "e": "1 ", "i": "1 ", "o": "2 ", "c": "4 ", "d": "4 ", "g": "4 ",
                 "k": "4 ", "n": "4 ", "s": "4 ", "t": "3 ", "x": "4 ", "y": "4 ", "z": "4 ",
                 "q": "5 ", "w": "5 ", "b": "6 ", "m": "6 ", "p": "6 ", "l": "7 ", "f": "8 ",
                 "v": "8 ", "j": "9 ", "r": "10 ", "h": "", "u": "2 "}  # define desired replacements here

        # use these three lines to do the replacement
        rep_1 = dict((re.escape(k), v) for k, v in rep_1.items())
        # Python 3 renamed dict.iteritems to dict.items so use rep_1.items() for latest versions
        pattern = re.compile("|".join(rep_1.keys()))
        text_index = pattern.sub(lambda m: rep_1[re.escape(m.group(0))], text_index)

        rep_2 = dict((re.escape(k), v) for k, v in rep_2.items())
        # Python 3 renamed dict.iteritems to dict.items so use rep_1.items() for latest versions
        pattern = re.compile("|".join(rep_2.keys()))
        text_index = pattern.sub(lambda m: rep_2[re.escape(m.group(0))], text_index).strip()

        mouth_ids = [int(num) for num in text_index.split(" ")]

        question_audio = gtts.gTTS(text=text, lang='en', slow=False)
        question_audio_file = 'consultation/question_audio_tmp/tempsave.mp3'
        question_audio.save(question_audio_file)

        pg.mixer.music.load(question_audio_file)
        pg.mixer.music.play()

        mouth_idx = 0
        if visual:
            display_screen.instruction = None

            # Keep in idle loop while speaking
            start = time.monotonic()
            while pg.mixer.music.get_busy():
                if time.monotonic() - start > 0.15:
                    display_screen.avatar.mouth_idx = mouth_ids[mouth_idx]
                    self.update_display(display_screen=display_screen, touch_screen=touch_screen)
                    start = time.monotonic()
                    mouth_idx += 1

            display_screen.avatar.mouth_idx = 0

            self.update_display(display_screen=display_screen, touch_screen=touch_screen)

    def get_relative_mose_pos(self):
        return pg.Vector2(pg.mouse.get_pos()) - pg.Vector2(0, self.display_size.y)

    def take_screenshot(self, filename=None):
        print("Taking Screenshot")
        img_array = pg.surfarray.array3d(self.window)
        img_array = cv2.transpose(img_array)
        img_array = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
        if filename is None:
            filename = datetime.datetime.now()
        cv2.imwrite(f"screenshots/{filename}.png", img_array)

    def entry_sequence(self):
        ...

    def exit_sequence(self):
        self.speak_text("The consultation is now complete. Thank you for your time")

        # PSS consult_record handling
        pss_answers = np.array(self.modules["PSS"].answers)
        if pss_answers.size > 0:
            pss_reverse_idx = np.array([3, 4, 6, 7])
            pss_reverse_idx = pss_reverse_idx[pss_reverse_idx < self.pss_question_count]
            pss_answers[pss_reverse_idx] = 4 - pss_answers[pss_reverse_idx]

        # Wisconsin Card Test consult_record handling
        WCT_score = self.modules["WCT"].engine.score

        # Spiral Test Handling
        spiral_data, spiral_size = self.modules["Spiral"].output
        spiral_data.to_csv('spiraldata.csv', index=False)

        spiral_image = pg.Surface(spiral_size, pg.SRCALPHA)  # create surface of correct size
        spiral_image.fill(Colours.white.value)  # fill with white background
        # draw in lines between each point recorded
        pg.draw.lines(spiral_image, Colours.black.value, False, spiral_data[["pixel_x", "pixel_y"]].to_numpy(), width=3)

        img_array = pg.surfarray.array3d(spiral_image)  # extract the pixel data from the pygame surface
        img_array = cv2.transpose(img_array)  # transpose to switch from pg to cv2 axis
        img_array = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)  # switch from RGB (pygame) to BGR (cv2) colours
        cv2.imwrite("consultation/response_data/spiral.png", img_array)  # Save image

        self.output = {
            "Consult_ID": self.id,
            "User_ID": self.user.id,
            "Date": date.today(),
            "PSS_Score": np.sum(pss_answers),
            "Wisconsin_Card_Score": WCT_score}

        shutil.rmtree("consultation/question_audio_tmp")

    def loop(self, infinite=False):
        self.entry_sequence()
        while self.running:
            for event in pg.event.get():
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE:
                        self.running = False

                    elif event.key == pg.K_s:
                        self.take_screenshot()

                elif event.type == pg.MOUSEBUTTONDOWN:
                    button_id = self.touch_screen.click_test(self.get_relative_mose_pos())
                    if button_id == 1:
                        self.touch_screen.kill_sprites()
                        self.update_display()
                        module = self.modules[self.module_order[self.module_idx]]
                        module.running = True
                        print("Entering Module Loop")
                        module.loop()
                        print("Exiting Module Loop")
                        self.display_screen.instruction = "Click the button to start"
                        self.update_display()
                        if infinite:
                            self.module_idx = (self.module_idx + 1) % len(self.modules)
                        else:
                            self.module_idx += 1
                            if self.module_idx == len(self.modules):
                                self.running = False

                        self.touch_screen.sprites = GameObjects([self.quit_button, self.main_button])
                        self.update_display()

                    elif button_id == 2:
                        self.running = False

                elif event.type == pg.QUIT:
                    self.running = False

        self.exit_sequence()


if __name__ == "__main__":
    os.environ['SDL_VIDEO_WINDOW_POS'] = "0,0"
    pg.init()
    consult = Consultation(pi=False, scale=0.7)
    consult.loop()

    if consult.output is not None:
        consult_record = pd.read_csv(
            "/Users/benhoskings/Library/CloudStorage/OneDrive-UniversityofWarwick/Documents/Engineering/Year 4/HERO/Data/consultation_record.tsv",
            delimiter="\t", index_col=0)
        consult_record.loc[consult.id] = consult.output

        consult_record.to_csv(
            "/Users/benhoskings/Library/CloudStorage/OneDrive-UniversityofWarwick/Documents/Engineering/Year 4/HERO/Data/consultation_record.tsv",
            sep="\t")

        # print(consult_record.head())
