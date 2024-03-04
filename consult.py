# import packages
import datetime
import json
import os
import os.path
import re
import shutil
import string
import time
from datetime import date, datetime

import cv2
import gtts
import numpy as np
import pandas as pd
import pygame as pg

from consultation.config import client

from db_access import DBClient

# import consultation modules
from consultation.modules.clock_draw import ClockDraw
from consultation.modules.perceived_stress_score import PSS
from consultation.modules.shape_searcher import ShapeSearcher
from consultation.modules.spiral_test import SpiralTest
from consultation.modules.visual_attention_test import VisualAttentionTest
from consultation.modules.wisconsin_card_test import CardGame
from consultation.modules.login_screen import LoginScreen
from consultation.modules.affective_computing import AffectiveModule
from consultation.modules.affective_computing_pi import AffectiveModulePi

# import graphics helpers
from consultation.utils import take_screenshot, NpEncoder
from consultation.screen import Colours, Fonts
from consultation.avatar import Avatar
from consultation.display_screen import DisplayScreen
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
    def __init__(self, enable_speech=True, scale=1, pi=True, authenticate=True, seamless=True,
                 username=None, password=None, consult_date=None, auto_run=False, wct_turns=20,
                 pss_questions=10, db_client=None, local=True):

        self.authenticate_user = authenticate
        self.user = None

        self.config = ConsultConfig(speech=enable_speech)
        if not os.path.isdir("consultation/question_audio_tmp"):
            os.mkdir("consultation/question_audio_tmp")

        self.display_size = pg.Vector2(1024, 600) * scale

        if os.path.exists("data/user_data.csv"):
            self.all_user_data = pd.read_csv("data/user_data.csv")
            self.all_user_data = self.all_user_data.set_index("Username")
        else:
            self.all_user_data = None

        # load all attributes which utilise any pygame surfaces!

        if pi:
            self.window = pg.display.set_mode((self.display_size.x, self.display_size.y * 2), pg.NOFRAME | pg.SRCALPHA)
        else:
            self.window = pg.display.set_mode((self.display_size.x, self.display_size.y * 2), pg.SRCALPHA)

        self.top_screen = self.window.subsurface(((0, 0), self.display_size))
        self.bottom_screen = self.window.subsurface((0, self.display_size.y), self.display_size)

        self.fonts = Fonts()
        self.display_screen = DisplayScreen(self.top_screen.get_size())
        self.touch_screen = TouchScreen(self.bottom_screen.get_size())
        button_size = pg.Vector2(300, 200)
        self.quit_button = GameButton((10, 10), pg.Vector2(70, 50), id=2, text="QUIT", colour=Colours.red)
        self.main_button = GameButton((self.display_size - button_size) /2, button_size, id=1, text="Start")

        self.avatar = Avatar(size=(self.display_size.y * 0.7, self.display_size.y * 0.7))
        self.display_screen.avatar = self.avatar

        self.pss_question_count = pss_questions

        self.auto_run = auto_run
        self.modules = {
            "Shapes": ShapeSearcher(parent=self, auto_run=auto_run),
            "Spiral": SpiralTest(turns=3, spiral_size=self.display_size.y*0.9, parent=self, auto_run=auto_run),
            "VAT": VisualAttentionTest(parent=self, grid_size=(self.display_size.y*0.9, self.display_size.y*0.9), auto_run=auto_run),
            "WCT": CardGame(parent=self, max_turns=wct_turns, auto_run=auto_run,),
            "PSS": PSS(parent=self, question_count=self.pss_question_count, auto_run=auto_run, preload_audio=False),
            "Clock": ClockDraw(parent=self, auto_run=self.auto_run),
            "Login": LoginScreen(parent=self, username=username, password=password, auto_run=auto_run),
            "Affective": AffectiveModulePi(parent=self, pi=pi, cleanse_files=False)
        }

        self.module_order = ["Spiral", "Clock", "Shapes", "VAT", "WCT", "PSS", "Affective"]
        # self.module_order = ["PSS", ]

        self.module_idx = 0

        self.output = None

        self.running = True

        self.seamless = seamless
        self.id = self.generate_unique_id()
        if consult_date:
            self.date = consult_date
        else:
            self.date = date.today()

        self.local = local
        if not local:
            if db_client is None:
                self.db_client = DBClient()
            else:
                self.db_client = db_client
        else:
            self.db_client = None

        self.pi = pi

        # self.update_display()
        # pg.event.pump()

    def generate_unique_id(self):
        letters = pd.Series(list(string.ascii_lowercase))[np.random.permutation(26)][:10].values
        numbers = np.random.permutation(10)[:5]
        num_pos = np.sort(np.random.permutation(range(1, 15))[:5])
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

        self.top_screen.blit(display_screen.get_surface(), (0, 0))
        self.bottom_screen.blit(touch_screen.get_surface(), (0, 0))
        pg.display.flip()

    def speak_text(self, text, visual=True, display_screen=None, touch_screen=None):
        if self.auto_run:
            return
        if not display_screen:
            display_screen = self.display_screen

        if not touch_screen:
            touch_screen = self.touch_screen

        text_index = text.lower()

        text_index = text_index.replace("?", "").replace("!", "").replace("“", "").replace("”", "")

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

        mouth_ids = []
        for num in text_index.split(" "):
            try:
                mouth_idx = int(num)
                mouth_ids.append(mouth_idx)

            except ValueError:
                pass

        question_audio = gtts.gTTS(text=text, lang='en', tld='com.au', slow=True)
        question_audio_file = 'consultation/question_audio_tmp/tempsave.mp3'
        question_audio.save(question_audio_file)

        pg.mixer.music.load(question_audio_file)
        pg.mixer.music.play()

        mouth_idx = 0
        if visual:
            temp_instruction = display_screen.instruction
            display_screen.instruction = None
            # Keep in idle loop while speaking
            start = time.monotonic()
            while pg.mixer.music.get_busy():
                if time.monotonic() - start > 0.15:
                    try:
                        display_screen.avatar.mouth_idx = mouth_ids[mouth_idx]
                        self.update_display(display_screen=display_screen, touch_screen=touch_screen)
                        start = time.monotonic()
                        mouth_idx += 1
                    except IndexError:
                        pass

            display_screen.avatar.mouth_idx = 0

            display_screen.instruction = temp_instruction
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
        if self.authenticate_user:
            self.user = self.modules["Login"].loop()

            self.speak_text(f"Welcome back {self.user.name}")

        if not self.seamless:
            self.touch_screen.sprites = GameObjects([self.quit_button, self.main_button])

            self.display_screen.instruction = "Click the button to start"
            self.update_display()

        if self.pi:
            print("Mouse invisible")
            pg.mouse.set_visible(False)

    def exit_sequence(self):
        self.speak_text("The consultation is now complete. Thank you for your time")

        # PSS consult_record handling
        pss_answers = np.array(self.modules["PSS"].answers)
        if pss_answers.size > 0:
            pss_reverse_idx = np.array([3, 4, 6, 7])
            pss_reverse_idx = pss_reverse_idx[pss_reverse_idx < self.pss_question_count]
            pss_answers[pss_reverse_idx] = 4 - pss_answers[pss_reverse_idx]



        pss_answers = {"answers": pss_answers.tolist()}
        # Wisconsin Card Test consult_record handling
        wct_answers = {"answers": self.modules["WCT"].engine.answers, "change_ids": self.modules["WCT"].engine.new_rule_ids}
        # Visual attention test
        vat_answers = {"answers": self.modules["VAT"].answers, "times": self.modules["VAT"].answer_times}

        clock_data = {"angle_errors": self.modules["Clock"].angle_errors}

        shape_data = {"scores": self.modules["Shapes"].scores,
                      "question_counts": self.modules["Shapes"].question_counts,
                      "answer_times": self.modules["Shapes"].answer_times}
        # Spiral Test Handling


        spiral_data = {"classification": int(self.modules["Spiral"].classification),
                       "value": self.modules["Spiral"].prediction}

        if self.user is None:
            user_id = None
        else:
            user_id = self.user.id

        self.output = {
            "consult_id": self.id,
            "user_id": int(user_id),
            "consult_time": self.date.strftime("%Y-%m-%d"),
            "consult_data": {
                "pss": pss_answers,
                "wct": wct_answers,
                "vat": vat_answers,
                "clock": clock_data,
                "shape": shape_data,
                "spiral": spiral_data
            }
        }

        base_path = "data"
        if self.user:
            if self.local:
                record_path = os.path.join(base_path, "consult_records")
                if not os.path.isdir(record_path):
                    os.mkdir(record_path)

                user_path = os.path.join(record_path, f"user_{self.user.id}")
                if not os.path.isdir(user_path):
                    os.mkdir(user_path)

                consult_path = os.path.join(user_path, f"consult_{self.id}")
                # records.insert_one(self.output)

                with open(consult_path, "w") as write_file:
                    json.dump(self.output, write_file, cls=NpEncoder, indent=4)  # encode dict into JSON

            else:
                self.db_client: DBClient
                self.db_client.upload_consult(self.output)
                records.insert_one(self.output)

        shutil.rmtree("consultation/question_audio_tmp")

        print(f"successfully completed consult {self.id}")

    def loop(self, infinite=False):
        self.entry_sequence()
        while self.running:
            if self.seamless:
                for module in self.module_order:
                    self.modules[module].loop()
                    self.update_display()

                self.running = False
            else:
                for event in pg.event.get():
                    if event.type == pg.KEYDOWN:
                        if event.key == pg.K_ESCAPE:
                            self.running = False

                        elif event.key == pg.K_s:
                            take_screenshot(self.window)

                    elif event.type == pg.MOUSEBUTTONDOWN:
                        button_id = self.touch_screen.click_test(self.get_relative_mose_pos())
                        if button_id == 1:
                            self.touch_screen.kill_sprites()
                            self.update_display()
                            module = self.modules[self.module_order[self.module_idx]]
                            module.running = True
                            module.loop()
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
        # return str(obj)


if __name__ == "__main__":
    os.environ['SDL_VIDEO_WINDOW_POS'] = "0,0"
    pg.init()
    pg.font.init()
    pg.event.pump()

    db = client.get_database('hero_data')
    records = db.user_records

    consult = Consultation(
        pi=False, authenticate=False, seamless=True, auto_run=False, username="benhoskings", password="pass", pss_questions=2
    )
    consult.loop()
