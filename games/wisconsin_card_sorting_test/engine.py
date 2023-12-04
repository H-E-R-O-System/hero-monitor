from enum import Enum
import pygame as pg
from models import *

rules = ['colour', 'shape', 'shape_count']

class CardGameEngine():

    def __init__(self):
        self.clock = pg.time.Clock()
        self.rule = random.choice(rules)
        self.score = 0
        self.turns = 0
        self.deal()

    def deal(self):
        self.deck = Deck(self.rule)
        self.deck.shuffle()

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


    def final_screen(self, screen):
        font = pg.font.Font(None, 36)
        screen.fill((255, 255, 255))
        text_surface = font.render('Game Completed!', True, (0, 0, 0))  # Green text
        text_rect = text_surface.get_rect(center=(512, 250))
        screen.blit(text_surface, text_rect)
        text_surface = font.render('Score: ' + str(self.score), True, (0, 0, 0))  # Green text
        text_rect = text_surface.get_rect(center=(512, 300))
        screen.blit(text_surface, text_rect)
        pg.display.flip() 
        