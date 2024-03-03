import math
import os
import random
import time

import pygame as pg

from consultation.display_screen import DisplayScreen
from consultation.screen import Colours, Fonts
from consultation.touch_screen import TouchScreen, GameObjects

from consultation.utils import take_screenshot


class AttentionCharacter(pg.sprite.Sprite):
    def __init__(self, size, text_surf, pos=(0, 0), odd=False):
        super().__init__()
        self.object_type = "card"
        self.image = pg.Surface(size)
        self.image.fill(Colours.lightGrey.value)
        self.rect = self.image.get_rect()
        self.image.blit(text_surf, (pg.Vector2(self.rect.size) - pg.Vector2(text_surf.get_size())) / 2)
        self.rect.topleft = pos
        self.odd = odd

    def is_clicked(self, pos):
        if self.rect.collidepoint(pos):
            return True
        else:
            return False

    def click_return(self):
        return self.odd


class VisualAttentionTest:
    def __init__(self, parent=None, size=(1024, 600), grid_size=(400, 400), auto_run=False):
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

            self.fonts = Fonts()

        self.display_screen.instruction = "Find the odd letter!"

        self.touch_screen = TouchScreen(self.display_size)
        self.grid_size = pg.Vector2(grid_size)
        self.grid_offset = (self.display_size - self.grid_size) / 2

        # Additional class properties
        self.clock = pg.time.Clock()
        self.grid_shape = pg.Vector2(4, 4)  # Specified as (col, row)
        self.grid_count = int(self.grid_shape.x * self.grid_shape.y)

        card_width, h_gap = math.pow(self.grid_shape.x + 1, -1), math.pow(self.grid_shape.x + 1, -2)
        card_height, v_gap = math.pow(self.grid_shape.y + 1, -1), math.pow(self.grid_shape.y + 1, -2)

        self.grid_positions = [
            (((idx % self.grid_shape.x) * card_width + ((idx % self.grid_shape.x) + 1) * h_gap) * self.grid_size.x,
             (math.floor(idx / self.grid_shape.y) * card_height + (
                     math.floor(idx / self.grid_shape.y) + 1) * v_gap) * self.grid_size.y)
            for idx in range(self.grid_count)]

        self.cell_size = pg.Vector2(card_width * self.grid_size.x, card_height * self.grid_size.y)

        self.max_rounds = 20

        self.score, self.total_time, self.rounds_played, self.correct_answers = 0, 0, 0, 0
        self.difficulty = 'easy'

        self.start_time = None

        self.common_letter = None
        self.odd_letter = None
        self.odd_idx = None
        self.characters = []

        self.answers = []
        self.answer_times = []

        # initialise module
        self.running = True
        self.auto_run = auto_run

    def select_letters(self):
        letters_easy = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        letters_medium = [('E', 'F'), ('W', 'V'), ('L', 'I')]
        letters_hard = [('u', 'ú'), ('b', 'd'), ('m', 'n')]

        if self.difficulty == 'easy':
            letters = letters_easy
        elif self.difficulty == 'medium':
            letter_pair = random.choice(letters_medium)
            letters = ''.join(letter_pair)
        elif self.difficulty == 'hard':
            letter_pair = random.choice(letters_hard)
            letters = ''.join(letter_pair)
        else:
            raise ValueError("Invalid difficulty level")

        self.common_letter = random.choice(letters)
        self.odd_letter = random.choice(letters.replace(self.common_letter, ''))

    def update_grid(self):
        self.touch_screen.kill_sprites()

        if self.parent:
            font = self.parent.fonts.normal
        else:
            font = self.fonts.normal

        grid_oddness = [0 for _ in range(self.grid_count)]
        grid_letters = [font.render(self.common_letter, False, Colours.black.value) for _ in range(self.grid_count)]

        self.odd_idx = random.randint(0, self.grid_count - 1)
        grid_oddness[self.odd_idx] = 1
        grid_letters[self.odd_idx] = font.render(self.odd_letter, False, Colours.black.value)

        self.characters = [AttentionCharacter(self.cell_size, letter, pos=pos + self.grid_offset, odd=odd) for letter, pos, odd in
                           zip(grid_letters, self.grid_positions, grid_oddness)]

        self.touch_screen.sprites = GameObjects(self.characters)
        self.update_display()

    def display_final_results(self, screen, score, average_time):
        screen.fill(Colours.black.value)
        font = pg.font.Font(None, 36)
        score_text = font.render(f"Final Score: {score}", True, Colours.white.value)
        time_text = font.render(f"Average Time: {average_time} milliseconds", True, Colours.white.value)
        score_rect = score_text.get_rect(center=(self.display_size.x // 2, self.display_size.y // 2 - 20))
        time_rect = time_text.get_rect(center=(self.display_size.x // 2, self.display_size.y // 2 + 20))
        screen.blit(score_text, score_rect)
        screen.blit(time_text, time_rect)
        pg.display.flip()

    def update_display(self):
        self.top_screen.blit(self.display_screen.get_surface(), (0, 0))
        self.bottom_screen.blit(self.touch_screen.get_surface(), (0, 0))
        pg.display.flip()

    def entry_sequence(self):
        if self.parent:
            self.parent.speak_text("Find the odd letter!", display_screen=self.display_screen,
                                   touch_screen=self.touch_screen)

        self.select_letters()
        self.update_grid()
        self.update_display()

        self.running = True
        self.start_time = time.monotonic()

    def exit_sequence(self):
        # post-loop completion section
        # maybe add short thank you for completing the section?

        # only OPTIONAL and can leave blank

        if self.auto_run:
            self.answer_times = [random.gauss(mu=1, sigma=0.1) for _ in range(len(self.answers))]

    def process_selection(self, selection):

        if selection:
            self.score += 1
            self.correct_answers += 1

        current_time = time.monotonic()
        self.answers.append(selection)
        self.answer_times.append(current_time - self.start_time)

        self.start_time = current_time

        # increase difficulty
        if self.correct_answers == 5:
            self.correct_answers = 0
            if self.difficulty == 'easy':
                self.difficulty = 'medium'
            elif self.difficulty == 'medium':
                self.difficulty = 'hard'

        self.rounds_played += 1
        if self.rounds_played == self.max_rounds:
            self.running = False
        else:
            self.select_letters()
            self.update_grid()

    def loop(self):
        self.entry_sequence()
        while self.running:
            if self.auto_run:
                # set 90% accuracy
                selection = random.randint(1, 10) > 1
                self.process_selection(selection)
            else:
                for event in pg.event.get():
                    if event.type == pg.KEYDOWN:
                        if event.key == pg.K_s:
                            # do something with key press
                            if self.parent:
                                take_screenshot(self.parent.window)
                            else:
                                take_screenshot(self.window, "visual_attention_test")

                        elif event.key == pg.K_ESCAPE:
                            self.running = False

                    elif event.type == pg.MOUSEBUTTONDOWN:
                        # do something with mouse click
                        pos = pg.Vector2(pg.mouse.get_pos()) - pg.Vector2(0, self.display_size.y)

                        selection = self.touch_screen.click_test(pos)
                        if selection is not None:
                            self.process_selection(selection)

                        pg.event.clear()

                    elif event.type == pg.QUIT:
                        # break the running loop
                        self.running = False

        self.exit_sequence()


if __name__ == "__main__":
    pg.init()
    pg.event.pump()
    os.chdir("/Users/benhoskings/Documents/Pycharm/Hero_Monitor")
    # Module Testing

    module_name = VisualAttentionTest(auto_run=False)
    module_name.loop()
    print("Module run successfully")

    print(module_name.answers, module_name.answer_times)
