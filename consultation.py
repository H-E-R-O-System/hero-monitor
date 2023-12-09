import pygame as pg
import cv2
import numpy as np
import pandas as pd
from datetime import date
import string

from consultation.screen import Screen, BlitLocation, Colours, Fonts
from consultation_lightweight import User, ConsultConfig
from consultation.display_screen import DisplayScreen
from consultation.touch_screen import TouchScreen
from consultation.avatar import Avatar
from consultation.perceived_stress_score import PSS

from games.spiral.spiral import SpiralTest


class Consultation:
    def __init__(self, user=None, enable_speech=True):

        if user:
            self.user = user
        else:
            # create demo user
            self.user = User("Demo", 65, 0)

        self.config = ConsultConfig(speech=enable_speech)

        self.display_size = pg.Vector2(1024, 600)

        # load all attributes which utilise any pygame surfaces!

        self.window = pg.display.set_mode((self.display_size.x, self.display_size.y * 2), pg.SRCALPHA)
        self.top_screen = self.window.subsurface(((0, 0), self.display_size))
        self.bottom_screen = self.window.subsurface((0, self.display_size.y), self.display_size)

        self.fonts = Fonts()
        self.display_screen = DisplayScreen(self.top_screen.get_size())
        self.display_screen.instruction = "Press S to Start"
        self.touch_screen = TouchScreen(self.bottom_screen.get_size())

        self.avatar = Avatar(size=(256, 256 * 1.125))

        self.pss_question_count = 1
        self.modules = [SpiralTest(0.8, 5, (600, 600), parent=self), PSS(self, question_count=self.pss_question_count), ]
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
        self.touch_screen.screen.refresh()
        self.display_screen.update()
        self.top_screen.blit(self.display_screen.get_surface(), (0, 0))
        self.bottom_screen.blit(self.touch_screen.get_surface(), (0, 0))
        pg.display.flip()

    def get_relative_mose_pos(self):
        return pg.Vector2(pg.mouse.get_pos()) - pg.Vector2(0, self.display_size.y)

    def take_screenshot(self):
        print("Taking Screenshot")
        img_array = pg.surfarray.array3d(self.window)
        img_array = cv2.transpose(img_array)
        img_array = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
        cv2.imwrite("screenshot.png", img_array)

    def entry_sequence(self):
        ...

    def exit_sequence(self):
        # PSS consult_record handling
        pss_answers = np.array(self.modules[1].answers)
        pss_reverse_idx = np.array([3, 4, 6, 7])
        pss_reverse_idx = pss_reverse_idx[pss_reverse_idx < self.pss_question_count]
        pss_answers[pss_reverse_idx] = 4 - pss_answers[pss_reverse_idx]

        # Wisconsin Card Test consult_record handling

        # Spiral Test Handling

        spiral_data = self.modules[0].create_dataframe()
        spiral_data.to_csv('spiraldata.csv', index=False)
        print("Spiral Data Written to CSV")

        self.output = {
            "Consult_ID": self.id,
            "User_ID": self.user.id,
            "Date": date.today(),
            "PSS_Score": np.sum(pss_answers),
            "Wisconsin_Card_Score": None}

    def loop(self):
        self.entry_sequence()
        while self.running:
            for event in pg.event.get():
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_s:
                        module = self.modules[self.module_idx]
                        module.running = True
                        print("Entering Module Loop")
                        module.loop()
                        print("Exiting Module Loop")
                        self.update_display()
                        self.module_idx = (self.module_idx + 1) % len(self.modules)

                    elif event.key == pg.K_x:
                        self.touch_screen.show_sprites = not self.touch_screen.show_sprites
                        self.update_display()

                # elif event.type == pg.MOUSEBUTTONDOWN:
                #     button_id = self.touch_screen.click_test(self.get_relative_mose_pos())

                elif event.type == pg.QUIT:
                    self.running = False

        self.exit_sequence()


if __name__ == "__main__":
    pg.init()
    consult = Consultation()
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
