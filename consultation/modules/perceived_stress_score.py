import os
import shutil

import gtts
import pygame as pg
from random import randint

from consultation.display_screen import DisplayScreen, Colours
from consultation.questions import Question, pss_questions
from consultation.touch_screen import TouchScreen, GameObjects, GameButton
from consultation.utils import Buttons, ButtonModule, take_screenshot
import numpy as np

import random


class PSS:
    def __init__(self, size=pg.Vector2(1024, 600), parent=None, question_count=10, auto_run=False, preload_audio=False,
                 record_video=False):
        self.parent = parent
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

        if not os.path.isdir("consultation/question_audio_tmp"):
            os.mkdir("consultation/question_audio_tmp")
        if not os.path.isdir("consultation/question_audio_tmp/pss"):
            os.mkdir("consultation/question_audio_tmp/pss")

        self.touch_screen = TouchScreen(size)

        gap = 10
        labels = ["Never", "Rarely", "Sometimes", "Often", "Always"]
        count = len(labels)

        self.likert_buttons = []
        for idx in range(count):
            width = (self.display_size.x - (count + 1) * gap) / count
            position = gap + idx * ((self.display_size.x - (count + 1) * gap) / count + gap)
            button = GameButton(pg.Vector2(position, (self.display_size.y - 150)/2), pg.Vector2(width, 150), idx, text=labels[idx],)
            self.likert_buttons.append(button)

        hints = ["" for _ in pss_questions]
        self.questions = [Question(question, hint) for question, hint in zip(pss_questions, hints)]
        self.questions = self.questions[:min(len(self.questions), question_count+1)]

        if preload_audio:
            self.preload_audio()

        self.question_order = np.random.permutation(range(len(self.questions)))
        self.question_idx = 0

        self.answers = []

        self.running = True
        self.awaiting_response = False
        self.auto_run = auto_run

        self.show_info = False
        self.power_off = False

    def preload_audio(self):
        exit_text = "Thank you for completing the PSS survey"
        exit_audio = gtts.gTTS(text=exit_text, lang='en', slow=False)
        exit_audio_file = f'consultation/question_audio_tmp/pss/exit.mp3'
        exit_audio.save(exit_audio_file)

        for idx, question in enumerate(self.questions):
            question_audio = gtts.gTTS(text=question.text, lang='en', slow=False)
            question_audio_file = f'consultation/question_audio_tmp/pss/question_{idx}.mp3'
            question_audio.save(question_audio_file)

    def update_display(self):
        self.display_screen.refresh()
        self.top_screen.blit(self.display_screen.get_surface(), (0, 0))
        self.bottom_screen.blit(self.touch_screen.get_surface(), (0, 0))
        pg.display.flip()

    def get_relative_mose_pos(self):
        return pg.Vector2(pg.mouse.get_pos()) - pg.Vector2(0, self.display_size.y)

    def ask_question(self, text=None):
        if not text:
            self.touch_screen.sprites = GameObjects(self.likert_buttons)

            question = self.questions[self.question_order[self.question_idx]]
            self.display_screen.instruction = None
            self.display_screen.speech_text = question.text
        else:
            question = None
            self.display_screen.instruction = "Section Complete"
            self.display_screen.speech_text = None

        self.update_display()

        if self.parent and question:
            self.parent.speak_text(question.text.replace("In the last month", ""), visual=True,
                                   display_screen=self.display_screen,
                                   touch_screen=self.touch_screen)

        if question:
            self.display_screen.instruction = "Select an option below"
        # self.display_screen.update(question=question)
        self.update_display()

    def entry_sequence(self):
        self.update_display()
        if self.parent:
            self.parent.speak_text("I will now ask some questions about how you have been feeling recently",
                                   display_screen=self.display_screen, touch_screen=self.touch_screen)

        self.update_display()

    def exit_sequence(self):
        if self.parent:
            self.parent.speak_text("Thank you for answering the questions")
        else:
            shutil.rmtree("consultation/question_audio_tmp")

    def button_actions(self, selected):

        if selected == Buttons.power:
            self.power_off = not self.power_off

            self.display_screen.power_off = self.power_off
            self.touch_screen.power_off = self.power_off
            self.update_display()

        else:
            ...
            print("Power")

    def loop(self, infinite=False):
        self.entry_sequence()

        mood = random.choice(range(5))

        while self.running:
            if not self.awaiting_response:
                self.ask_question()
                self.awaiting_response = True
                pg.event.clear()

            elif self.awaiting_response and self.auto_run:
                # select random button within button range
                mood_weights = [1, 1, 1, 1, 1]
                # print(mood)
                if self.question_idx in [3, 4, 6, 7]:
                    mood_weights[4-mood] = 5
                else:
                    mood_weights[mood] = 5

                button_idx = random.choices(range(len(self.touch_screen.sprites)), weights=mood_weights, k=1)
                button_id = self.touch_screen.sprites.sprites()[button_idx[0]].id

                self.answers.append(int(button_id))

                if infinite:
                    self.question_idx = (self.question_idx + 1) % len(self.questions)
                else:
                    self.question_idx += 1

                self.update_display()
                self.awaiting_response = False

                if self.question_idx == len(self.questions):
                    self.running = False

            else:
                for event in pg.event.get():
                    if event.type == pg.KEYDOWN and not self.power_off:
                        if event.key == pg.K_ESCAPE:
                            self.running = False

                        elif event.key == pg.K_s:
                            if self.parent:
                                take_screenshot(self.parent.window)
                            else:
                                take_screenshot(self.window, "perceived_stress_score")

                    elif event.type == pg.MOUSEBUTTONDOWN and not self.power_off:
                        pos = pg.Vector2(pg.mouse.get_pos()) - pg.Vector2(0, self.display_size.y)
                        button_id = self.touch_screen.click_test(pos)
                        if button_id is not None and self.awaiting_response:
                            self.answers.append(int(button_id))
                            if infinite:
                                self.question_idx = (self.question_idx + 1) % len(self.questions)
                            else:
                                self.question_idx += 1

                            self.update_display()
                            self.awaiting_response = False

                            if self.question_idx == len(self.questions):
                                self.running = False

                        pg.event.clear()

                    elif event.type == pg.QUIT:
                        self.running = False

                selected = self.button_module.check_pressed()
                if selected is not None:
                    self.button_actions(selected)

        self.exit_sequence()


if __name__ == "__main__":
    pg.init()
    pg.event.pump()
    os.chdir("../..")

    pss = PSS(auto_run=True, question_count=10)
    pss.loop()

    answers = pss.answers
    answers = np.array(answers)
    pss_reverse_idx = np.array([3, 4, 6, 7])
    pss_reverse_idx = pss_reverse_idx[pss_reverse_idx < pss.question_idx]
    answers[pss_reverse_idx] = 4 - answers[pss_reverse_idx]

    print(answers)