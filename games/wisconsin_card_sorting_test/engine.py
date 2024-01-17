from enum import Enum
import pygame as pg
from games.wisconsin_card_sorting_test.models import *

rules = ['colour', 'shape', 'shape_count']

class CardGameEngine():

    def __init__(self, quiz_coord, option_coords):
        self.clock = pg.time.Clock()
        self.rule = random.choice(rules)
        print(self.rule)
        self.score = 0
        self.turns = 0
        self.quiz_coord = quiz_coord
        self.option_coords = option_coords
        self.deck = None

        self.deal()

    def deal(self):
        self.deck = Deck(self.rule)
        self.deck.quiz_card.rect.topleft = self.quiz_coord
        self.deck.shuffle()
        for idx, card in enumerate(self.deck.cards):
            card.rect.topleft = self.option_coords[idx]
        self.deck.update()

    def correct_selection(self, screen):
        self.score += 1
        self.selection_result_screen(screen, 'Correct!', (0, 255, 0))

    def incorrect_selection(self, screen):
        self.selection_result_screen(screen, 'Incorrect', (255, 0, 0))

    def selection_result_screen(self, screen, text, text_colour):
        start_time = pg.time.get_ticks()
        duration = 2000
        font = pg.font.Font(None, 60)

        while pg.time.get_ticks() - start_time <= duration:
            screen.fill((255, 255, 255))
            text_surface = font.render(text, True, text_colour)  # Green text
            text_rect = text_surface.get_rect(center=(512, 300))
            screen.blit(text_surface, text_rect)
            pg.display.flip()
            self.clock.tick(60)
        