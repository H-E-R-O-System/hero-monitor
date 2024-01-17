from enum import Enum
import pygame as pg
from games.wisconsin_card_sorting_test.models import *

rules = ['colour', 'shape', 'shape_count']


class CardGameEngine:
    def __init__(self, quiz_coord, option_coords, card_size=(164, 214)):
        self.rule = random.choice(rules)
        print(self.rule)
        self.score = 0
        self.turns = 0
        self.card_size = card_size
        self.quiz_coord = quiz_coord
        self.option_coords = option_coords
        self.deck = None

        self.deal()

    def deal(self):
        self.deck = Deck(self.rule, card_size=self.card_size)
        self.deck.quiz_card.rect.topleft = self.quiz_coord
        self.deck.shuffle()
        for idx, card in enumerate(self.deck.cards):
            card.rect.topleft = self.option_coords[idx]
        self.deck.update()
        