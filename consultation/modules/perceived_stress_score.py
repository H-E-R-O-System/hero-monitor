import pygame as pg
import time
import os
import gtts
from consultation.questions import Question, pss_questions
from consultation.touch_screen import TouchScreen, GameObjects, GameButton
from consultation.display_screen import DisplayScreen, DisplayScreenV2


class PSS:
    def __init__(self, parent, question_count=10):
        self.parent = parent
        if not os.path.isdir("consultation/question_audio_tmp/pss"):
            os.mkdir("consultation/question_audio_tmp/pss")

        self.display_size = self.parent.display_size

        self.top_screen: pg.Surface = parent.top_screen
        self.bottom_screen: pg.Surface = parent.bottom_screen

        self.touch_screen = TouchScreen(self.top_screen.get_size())
        self.display_screen = DisplayScreenV2(self.bottom_screen.get_size(), info_height=0.2)
        self.display_screen.avatar = parent.display_screen.avatar
        count = 5

        gap = 10
        labels = ["Never", "Almost Never", "Sometimes", "Very Often", "Always"]

        self.likert_buttons = []
        for idx in range(count):
            width = (self.display_size.x - (count + 1) * gap) / count
            position = gap + idx * ((self.display_size.x - (count + 1) * gap) / count + gap)
            button = GameButton(pg.Vector2(position, self.display_size.y/2), pg.Vector2(width, 50), idx, text=str(idx),
                                label=labels[idx])
            self.likert_buttons.append(button)

        if parent:
            self.display_screen.avatar = parent.display_screen.avatar

        hints = ["" for _ in pss_questions]
        self.questions = [Question(question, hint) for question, hint in zip(pss_questions, hints)]
        self.questions = self.questions[:min(len(self.questions)-1, question_count)]

        self.preload_audio()

        self.question_idx = 0

        self.answers = []

        self.running = True
        self.awaiting_response = False

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

        if self.question_idx < len(self.questions):
            question_audio_file = f'consultation/question_audio_tmp/pss/question_{str(self.question_idx)}.mp3'
        else:
            question_audio_file = f'consultation/question_audio_tmp/pss/exit.mp3'

        pg.mixer.music.load(question_audio_file)
        pg.mixer.music.play()

        # Keep in idle loop while speaking
        self.display_screen.avatar.state = 1
        start = time.monotonic()
        while pg.mixer.music.get_busy():
            if time.monotonic() - start > 0.15:
                # self.display_screen.update(question=question)
                self.update_display()
                self.display_screen.avatar.speak_state = (self.display_screen.avatar.speak_state + 1) % 2
                start = time.monotonic()

        self.display_screen.avatar.state = 0

        if question:
            self.display_screen.instruction = "Select an option below"
        # self.display_screen.update(question=question)
        self.update_display()

    def entry_sequence(self):
        self.update_display()

    def exit_sequence(self):
        self.parent.speak_text("Thank you for completing the PSS module")

    def loop(self, infinite=False):
        self.entry_sequence()

        while self.running:
            if not self.awaiting_response:
                self.ask_question()
                self.awaiting_response = True

            for event in pg.event.get():
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE:
                        self.running = False

                    elif event.key == pg.K_w:
                        self.parent.take_screenshot("pss")

                elif event.type == pg.MOUSEBUTTONDOWN:
                    button_id = self.touch_screen.click_test(self.parent.get_relative_mose_pos())
                    if button_id is not None and self.awaiting_response:
                        self.answers.append(int(button_id))
                        if infinite:
                            self.question_idx = (self.question_idx + 1) % len(self.questions)
                        else:
                            self.question_idx += 1

                        self.update_display()
                        self.awaiting_response = False

                        if self.question_idx == len(self.questions):
                            print("stop")
                            self.running = False

                elif event.type == pg.QUIT:
                    self.running = False

        self.exit_sequence()