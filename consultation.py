# import packages
import datetime
import os.path

import cv2
import gtts
import os
import string
import shutil
import time
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
    def __init__(self, user=None, enable_speech=True, scale=1, full_screen=False):
        pi = True

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

        if full_screen:
            pg.display.toggle_fullscreen()

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

        self.avatar = Avatar(size=(320, 320 * 1.125))
        self.display_screen.avatar = self.avatar

        self.pss_question_count = 3
        self.modules = {
            "Shapes": ShapeSearcher(max_turns=10, parent=self),
            "Spiral": SpiralTest(turns=3, touch_size=(self.display_size.y*0.9, self.display_size.y*0.9), parent=self),
            "VAT": VisualAttentionTest(touch_size=(self.display_size.y*0.9, self.display_size.y*0.9), parent=self),
            "WCT": CardGame(max_turns=8, parent=self),
            "PSS": PSS(self, question_count=self.pss_question_count),
        }

        self.module_order = ["PSS", "Spiral", "Shapes", "VAT", "WCT", "PSS"]

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

    def update_display(self):
        self.touch_screen.refresh()
        self.display_screen.update()

        self.top_screen.blit(self.display_screen.get_surface(), (0, 0))
        self.bottom_screen.blit(self.touch_screen.get_surface(), (0, 0))
        pg.display.flip()

    def speak_text(self, text, visual=True):
        question_audio = gtts.gTTS(text=text, lang='en', slow=False)
        question_audio_file = 'consultation/question_audio_tmp/tempsave.mp3'
        question_audio.save(question_audio_file)

        pg.mixer.music.load(question_audio_file)
        pg.mixer.music.play()
        if visual:
            self.display_screen.instruction = None
            self.display_screen.update()

            # Keep in idle loop while speaking
            self.display_screen.avatar.state = 1
            start = time.monotonic()
            while pg.mixer.music.get_busy():
                if time.monotonic() - start > 0.15:
                    self.display_screen.update()
                    self.update_display()
                    self.display_screen.avatar.speak_state = (self.display_screen.avatar.speak_state + 1) % 2
                    start = time.monotonic()

            self.display_screen.avatar.state = 0

            self.display_screen.update()
            self.update_display()

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
    consult = Consultation(full_screen=False)
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
