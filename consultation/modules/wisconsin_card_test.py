import time

import pygame as pg
import os
import random

from consultation.touch_screen import GameObjects, TouchScreen
from consultation.display_screen import DisplayScreen
from consultation.screen import Colours, BlitLocation
import math

colours = ['red', 'blue', 'green', 'yellow']
shapes = ['square', 'circle', 'triangle', 'diamond']
rules = ['colour', 'shape', 'shape_count']


class Card(pg.sprite.Sprite):
    def __init__(self, deck, size, colour=None, shape=None, shape_count=None, quiz_card=False):
        super().__init__()
        self.object_type = "card"
        self.size = pg.Vector2(size)
        self.rect = pg.Rect((0, 0), self.size)
        self.shape = shape
        self.shape_count = shape_count
        self.quiz_card = quiz_card

        # if the attribute that is the current rule has been given, this card is set as 'correct':
        if (deck.rule == 'colour' and colour) or (deck.rule == 'shape' and shape) or (
                deck.rule == 'shape_count' and shape_count):
            self.correct = True
        else:
            self.correct = False

        # making sure that each card represents maximum and minimum of 1 quiz card attribute
        if colour:
            self.colour = Colours[colour]
        else:
            self.colour = Colours[random.choice(list(set(colours) - {deck.quiz_colour}))]
        if not shape:
            self.shape = random.choice(list(set(shapes) - {deck.quiz_shape}))
        if not shape_count:
            self.shape_count = random.choice(list({1, 2, 3} - {deck.quiz_shape_count}))

        self.image = self.render_image()

    def render_image(self):
        surf = pg.Surface(self.size)
        surf.fill(Colours.white.value)
        pg.draw.rect(surf, Colours.lightGrey.value, surf.get_rect(), width=7)

        shape_size = min(self.size.x, self.size.y) // 5
        spacing = (self.size.x - (self.shape_count * shape_size)) // (self.shape_count + 1)

        for i in range(self.shape_count):
            x = spacing + i * (spacing + shape_size)
            y = self.size.y // 2

            if self.shape == 'triangle':
                pg.draw.polygon(surf, self.colour.value, [(x, y - shape_size // 2),
                                                          (x + shape_size, y - shape_size // 2),
                                                          (x + shape_size // 2, y + shape_size // 2)])
            elif self.shape == 'circle':
                pg.draw.circle(surf, self.colour.value, (x + shape_size // 2, y), shape_size // 2)
            elif self.shape == 'square':
                pg.draw.rect(surf, self.colour.value, (x, y - shape_size // 2, shape_size, shape_size))
            elif self.shape == 'diamond':
                pg.draw.polygon(surf, self.colour.value, [(x, y),
                                                          (x + shape_size // 2, y - shape_size // 2),
                                                          (x + shape_size, y),
                                                          (x + shape_size // 2, y + shape_size // 2)])
        return surf

    def is_clicked(self, pos):
        if self.quiz_card:
            return None
        elif self.rect.collidepoint(pos):
            return True
        else:
            return False

    def click_return(self):
        return self.correct


class Deck:
    def __init__(self, rule, card_size):
        self.rule = rule
        self.quiz_shape = random.choice(shapes)
        self.quiz_colour = random.choice(colours)
        self.quiz_shape_count = random.randint(1, 3)
        self.quiz_card = Card(deck=self, size=card_size, shape=self.quiz_shape,
                              colour=self.quiz_colour, shape_count=self.quiz_shape_count, quiz_card=True)

        self.cards = []
        self.cards.append(Card(deck=self, size=card_size, shape=self.quiz_shape))
        self.cards.append(Card(deck=self, size=card_size, colour=self.quiz_colour))
        self.cards.append(Card(deck=self, size=card_size, shape_count=self.quiz_shape_count))

        self.all_cards = [*self.cards.copy(), self.quiz_card]

    def shuffle(self):
        random.shuffle(self.cards)

    def update(self):
        self.all_cards = [*self.cards.copy(), self.quiz_card]

class CardGameEngine:
    def __init__(self, quiz_coord, option_coords, card_size=(164, 214)):
        self.rule = random.choice(rules)
        print(f"Game rule: {self.rule}")
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
        self.display_screen.instruction = "Match the card!"
        self.touch_screen = TouchScreen(self.display_size, colour=Colours.white.value)

        if parent:
            self.display_screen.avatar = parent.display_screen.avatar

        self.running = True

        # Card positioning in the screen. The positions specify the center of the card.
        option_count = 3
        card_width, h_gap = math.pow(option_count + 1, -1), math.pow(option_count + 1, -2)
        card_height, v_gap = math.pow(3, -1), math.pow(3, -2)

        self.quiz_coord = (0.5 * self.display_size.x * (1 - card_width), v_gap * self.display_size.y)
        self.option_coords = [((idx * card_width + (idx + 1) * h_gap) * self.display_size.x,
                               (card_height + 2 * v_gap) * self.display_size.y)
                              for idx in range(option_count)]

        self.engine = CardGameEngine(self.quiz_coord, self.option_coords,
                                     card_size=(self.display_size.x / 4, self.display_size.y / 3))

        self.max_turns = max_turns

    def render_game(self):
        # clear game screens
        self.touch_screen.refresh()
        # update game screens
        self.display_screen.update()
        self.touch_screen.sprites = GameObjects(self.engine.deck.all_cards)

        self.update_displays()

    def display_message(self, answer):
        self.touch_screen.refresh()
        self.touch_screen.kill_sprites()
        if answer:
            self.touch_screen.add_text("Correct!", pos=self.display_size / 2, location=BlitLocation.centre)
        else:
            self.touch_screen.add_text("Incorrect!", pos=self.display_size / 2, location=BlitLocation.centre)

        self.update_displays()
        time.sleep(1)

    def update_displays(self):
        if self.parent:
            self.top_screen.blit(self.display_screen.get_surface(), (0, 0))

        self.bottom_screen.blit(self.touch_screen.get_surface(), (0, 0))
        pg.display.flip()

    def entry_sequence(self):
        self.render_game()
        if self.parent:
            self.parent.speak_text("Please match the card", visual=False)

    def exit_sequence(self):
        self.touch_screen.refresh()
        self.touch_screen.kill_sprites()
        self.touch_screen.add_text("Game Completed!", pos=self.display_size / 2, location=BlitLocation.centre)
        self.touch_screen.add_text('Score: ' + str(self.engine.score),
                                          pos=(self.display_size / 2) + pg.Vector2(0, 50),
                                          location=BlitLocation.centre)
        self.update_displays()
        time.sleep(1)
        self.running = False

    def loop(self):
        self.entry_sequence()
        while self.running:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.running = False

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
                            self.running = False
                        else:
                            self.engine.deal()
                            self.render_game()

                elif event.type == pg.KEYDOWN:
                    if event.key == pg.K_w:
                        if self.parent:
                            self.parent.take_screenshot()

        self.exit_sequence()


if __name__ == "__main__":
    os.chdir("/Users/benhoskings/Documents/Pycharm/Hero_Monitor")
    pg.init()
    card_game = CardGame(max_turns=3)
    card_game.loop()
    print("Card game ran successfully")