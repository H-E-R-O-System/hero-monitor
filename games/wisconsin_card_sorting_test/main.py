import time

import pygame as pg
from games.wisconsin_card_sorting_test.models import *
from games.wisconsin_card_sorting_test.engine import *
import os

from consultation.touch_screen import TouchScreen, GameObjects
from consultation.display_screen import DisplayScreen
from consultation.screen import Colours, BlitLocation


class CardGame:

    def __init__(self, size=(1024, 600), max_turns=10, parent=None):
        self.parent = parent

        if parent is not None:
            self.display_size = parent.display_size
            self.bottom_screen = parent.bottom_screen
            self.top_screen = parent.top_screen
        else:
            self.display_size = pg.Vector2(size)
            self.bottom_screen = pg.display.set_mode(self.display_size)
            self.top_screen = None

        self.display_screen = DisplayScreen(self.display_size)
        self.touch_screen = TouchScreen(self.display_size)
        self.touch_screen.show_sprites = True

        if parent:
            self.display_screen.avatar.face_colour = parent.display_screen.avatar.face_colour
            self.display_screen.avatar.update_colours()
            
        self.running = True
        pg.display.set_caption('Wisconsin Card Sorting Test')
        self.quiz_coord = (450, 50)
        self.option_coords = [(150, 325), (450, 325), (750, 325)]

        self.engine = CardGameEngine(self.quiz_coord, self.option_coords)

        self.max_turns = max_turns

    def render_game(self):
        # print(self.engine.deck.all_cards)
        self.touch_screen.refresh()
        self.touch_screen.sprites = GameObjects(self.engine.deck.all_cards)
        self.update_displays()

    def display_message(self, answer):
        self.touch_screen.refresh()
        self.touch_screen.kill_sprites()
        if answer:
            self.touch_screen.screen.add_text("Correct!", pos=self.display_size/2, location=BlitLocation.centre)
        else:
            self.touch_screen.screen.add_text("Incorrect!", pos=self.display_size / 2, location=BlitLocation.centre)

        self.update_displays()
        time.sleep(1)

    def update_displays(self):
        if self.parent:
            self.top_screen.blit(self.display_screen.get_surface(), (0, 0))

        self.bottom_screen.blit(self.touch_screen.get_surface(), (0, 0))
        pg.display.flip()

    def entry_sequence(self):
        self.render_game()

    def exit_sequence(self):
        self.touch_screen.refresh()
        self.touch_screen.kill_sprites()
        self.touch_screen.screen.add_text("Game Completed!", pos=self.display_size / 2, location=BlitLocation.centre)
        self.touch_screen.screen.add_text('Score: ' + str(self.engine.score),
                                          pos=(self.display_size / 2) + pg.Vector2(0, 50),
                                          location=BlitLocation.centre)
        self.update_displays()
        time.sleep(2)
        self.running = False

    def loop(self):
        game_over = False
        self.entry_sequence()
        while self.running:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.running = False
                elif game_over:
                    self.exit_sequence()
                elif event.type == pg.MOUSEBUTTONDOWN:
                    if self.parent:
                        pos = self.parent.get_relative_mose_pos()
                    else:
                        pos = pg.mouse.get_pos()
                    selection = self.touch_screen.click_test(pos)
                    if selection is not None:
                        self.display_message(selection)

                        if selection:
                            self.engine.score += 1

                        self.engine.turns += 1
                        if self.engine.turns == self.max_turns:
                            game_over = True
                        else:
                            self.engine.deal()

                    if not game_over:
                        self.render_game()

if __name__ == "__main__":
    os.chdir("/Users/benhoskings/Documents/Pycharm/Hero_Monitor")
    pg.init()
    card_game = CardGame()
    card_game.loop()
    print("Card game ran successfully")