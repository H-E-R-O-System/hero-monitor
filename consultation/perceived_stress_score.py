import pygame as pg
import time
import gtts
from consultation.questions import Question, pss_questions
from consultation.touch_screen import TouchScreen
from consultation.display_screen import DisplayScreen


class PSS:
    def __init__(self, parent, question_count=10):
        self.parent = parent
        self.display_size = pg.Vector2(1024, 600)

        self.top_screen: pg.Surface = parent.top_screen
        self.bottom_screen: pg.Surface = parent.bottom_screen

        self.touch_screen = TouchScreen(self.top_screen.get_size())
        self.display_screen = DisplayScreen(self.bottom_screen.get_size())

        self.touch_screen.show_sprites = True

        hints = ["" for _ in pss_questions]
        self.questions = [Question(question, hint) for question, hint in zip(pss_questions, hints)]
        self.questions = self.questions[:min(len(self.questions)-1, question_count)]
        self.question_idx = 0

        self.answers = []

        self.running = True
        self.awaiting_response = False

    def update_display(self):
        self.top_screen.blit(self.display_screen.get_surface(), (0, 0))
        self.bottom_screen.blit(self.touch_screen.get_surface(), (0, 0))
        pg.display.flip()

    def get_relative_mose_pos(self):
        return pg.Vector2(pg.mouse.get_pos()) - pg.Vector2(0, self.display_size.y)

    def ask_question(self, text=None):
        if not text:
            self.touch_screen.load_likert_buttons(height=275)
            question = self.questions[self.question_idx]
            text = question.text
            self.display_screen.instruction = None
            self.display_screen.update(question)
        else:
            question=None
            self.display_screen.instruction = "Section Complete"
            self.display_screen.update()

        self.question_audio = gtts.gTTS(text=text, lang='en', slow=False)
        question_audio_file = f'consultation/question_audio/tempsave_question_{str(self.question_idx)}.mp3'
        self.question_audio.save(question_audio_file)

        pg.mixer.music.load(question_audio_file)
        pg.mixer.music.play()

        # Keep in idle loop while speaking
        self.display_screen.avatar.state = 1
        start = time.monotonic()
        while pg.mixer.music.get_busy():
            if time.monotonic() - start > 0.15:
                self.display_screen.update(question=question)
                self.update_display()
                self.display_screen.avatar.speak_state = (self.display_screen.avatar.speak_state + 1) % 2
                start = time.monotonic()

        self.display_screen.avatar.state = 0

        if question:
            self.display_screen.instruction = "Select an option below"
        self.display_screen.update(question=question)
        self.update_display()

    def entry_sequence(self):
        self.update_display()

    def exit_sequence(self):
        messages = ["Thank you for completing the PSS module",
                    "The next module will be the spiral test"]
        self.touch_screen.kill_sprites()
        for message in messages:
            self.ask_question(message)

    def loop(self, infinite=False):
        self.entry_sequence()

        while self.running:
            if not self.awaiting_response:
                self.ask_question()
                self.awaiting_response = True

            for event in pg.event.get():
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_x:
                        self.touch_screen.show_sprites = not self.touch_screen.show_sprites
                        self.update_display()

                    elif event.key == pg.K_ESCAPE:
                        self.running = False

                    elif event.key == pg.K_w:
                        self.parent.take_screenshot()

                elif event.type == pg.MOUSEBUTTONDOWN:
                    button_id = self.touch_screen.click_test(self.get_relative_mose_pos())
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