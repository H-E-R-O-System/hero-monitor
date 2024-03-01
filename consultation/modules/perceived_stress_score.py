import os
import shutil

import gtts
import pygame as pg
from random import randint

from consultation.display_screen import DisplayScreen
from consultation.questions import Question, pss_questions
from consultation.touch_screen import TouchScreen, GameObjects, GameButton


class PSS:
    def __init__(self, size=pg.Vector2(1024, 600), parent=None, question_count=10, auto_run=False, preload_audio=True):
        self.parent = parent
        self.parent = parent
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

        if not os.path.isdir("consultation/question_audio_tmp"):
            os.mkdir("consultation/question_audio_tmp")
        if not os.path.isdir("consultation/question_audio_tmp/pss"):
            os.mkdir("consultation/question_audio_tmp/pss")

        self.touch_screen = TouchScreen(size)

        gap = 10
        labels = ["Never", "Almost Never", "Sometimes", "Very Often", "Always"]
        count = len(labels)

        self.likert_buttons = []
        for idx in range(count):
            width = (self.display_size.x - (count + 1) * gap) / count
            position = gap + idx * ((self.display_size.x - (count + 1) * gap) / count + gap)
            button = GameButton(pg.Vector2(position, self.display_size.y/2), pg.Vector2(width, 50), idx, text=labels[idx],)
            self.likert_buttons.append(button)

        hints = ["" for _ in pss_questions]
        self.questions = [Question(question, hint) for question, hint in zip(pss_questions, hints)]
        self.questions = self.questions[:min(len(self.questions), question_count+1)]

        if preload_audio:
            self.preload_audio()

        self.question_idx = 0

        self.answers = []

        self.running = True
        self.awaiting_response = False
        self.auto_run = auto_run

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

            question = self.questions[self.question_idx]
            self.display_screen.instruction = None
            self.display_screen.speech_text = question.text
        else:
            question = None
            self.display_screen.instruction = "Section Complete"
            self.display_screen.speech_text = None

        self.update_display()

        if self.parent:
            self.parent.speak_text(self.questions[self.question_idx].text.replace("In the last month", ""), visual=True,
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
            self.parent.speak_text("Thank you for completing the PSS module")
        else:
            shutil.rmtree("consultation/question_audio_tmp")

    def loop(self, infinite=False):
        self.entry_sequence()

        while self.running:
            if not self.awaiting_response:
                self.ask_question()
                self.awaiting_response = True

            elif self.awaiting_response and self.auto_run:
                # select random button within button range
                button_idx = randint(0, len(self.touch_screen.sprites)-1)
                button_id = self.touch_screen.sprites.sprites()[button_idx].id

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
                    if event.type == pg.KEYDOWN:
                        if event.key == pg.K_ESCAPE:
                            self.running = False

                        elif event.key == pg.K_w:
                            self.parent.take_screenshot("pss")

                    elif event.type == pg.MOUSEBUTTONDOWN:
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

                    elif event.type == pg.QUIT:
                        self.running = False

        self.exit_sequence()


if __name__ == "__main__":
    pg.init()
    pg.event.pump()
    os.chdir("/Users/benhoskings/Documents/Pycharm/Hero_Monitor")

    pss = PSS()
    pss.loop()