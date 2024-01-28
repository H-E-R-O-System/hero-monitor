import time

import pygame as pg
import os
import random

from consultation.touch_screen import GameObjects, TouchScreen, GameButton
from consultation.display_screen import DisplayScreenV2
from consultation.screen import Colours, BlitLocation
import math
import cv2

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

    def deal(self, option_coords=None):
        self.deck = Deck(self.rule, card_size=self.card_size)
        self.deck.quiz_card.rect.topleft = self.quiz_coord
        self.deck.shuffle()
        if option_coords:
            for idx, card in enumerate(self.deck.cards):
                card.rect.topleft = option_coords[idx]
        else:
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

        self.display_screen = DisplayScreenV2(self.display_size)
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

    def instruction_loop(self):
        self.display_screen.state = 1
        self.display_screen.instruction = None

        button_rect = pg.Rect(self.display_size.x / 2 - 50, self.display_size.y - 120, 100, 100)
        start_button = GameButton(position=button_rect.topleft, size=button_rect.size, text="START", id=1)
        self.touch_screen.sprites = GameObjects([start_button])
        info_rect = pg.Rect(0.3 * self.display_size.x, 0, 0.7 * self.display_size.x, 0.8 * self.display_size.y)
        pg.draw.rect(self.display_screen.surface, Colours.white.value,
                     info_rect)

        self.display_screen.add_multiline_text("Match The Card!", rect=info_rect.scale_by(0.9, 0.9),
                                               font_size="large")

        self.display_screen.add_multiline_text(
            rect=info_rect.scale_by(0.9, 0.9), text=
            "Match the top card to one of the three below it. There is one rule which determines if the the card is a "
            "match. This could be color, shape or number of shapes. An example is shown below, where the 'Rule' is that"
            " cards with the same colour match. You must first work out the rule, and then use this to answer each "
            "question",
            center_vertical=True)

        question_rect = pg.Rect(0.05 * self.display_size.x, 0.05 * self.display_size.y, 0.4 * self.display_size.x,
                                0.9 * self.display_size.y)
        answer_rect = pg.Rect((0.55 * self.display_size.x, 0.05 * self.display_size.y), question_rect.size)
        self.touch_screen.load_image("consultation/graphics/instructions/wct_question.png",
                                     size=question_rect.size,
                                     pos=question_rect.topleft)
        # pg.draw.rect(self.touch_screen.surface, Colours.lightGrey.value, question_rect, width=3)

        self.touch_screen.add_multiline_text("Question",
                                             pg.Rect(question_rect.topleft, (question_rect.w, 0.08 * question_rect.h)),
                                             center_horizontal=True, center_vertical=True,
                                             bg_colour=Colours.lightGrey)

        self.touch_screen.load_image("consultation/graphics/instructions/wct_answer.png",
                                     size=answer_rect.size,
                                     pos=answer_rect.topleft)
        # pg.draw.rect(self.touch_screen.surface, Colours.lightGrey.value, answer_rect, width=3)
        self.touch_screen.add_multiline_text(
            "Answer", pg.Rect(answer_rect.topleft, (answer_rect.w, 0.08 * answer_rect.h)),
            center_horizontal=True, center_vertical=True, bg_colour=Colours.lightGrey)

        self.update_displays()
        wait = True
        while wait:
            for event in pg.event.get():
                if event.type == pg.MOUSEBUTTONDOWN:
                    if self.parent:
                        pos = self.parent.get_relative_mose_pos()
                    else:
                        pos = pg.mouse.get_pos()

                    selection = self.touch_screen.click_test(pos)
                    if selection is not None:
                        wait = False

                elif event.type == pg.KEYDOWN:
                    if event.key == pg.K_w:
                        if self.parent:
                            self.parent.take_screenshot()
                        else:
                            img_array = pg.surfarray.array3d(self.touch_screen.get_surface())
                            img_array = cv2.transpose(img_array)
                            img_array = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
                            cv2.imwrite("screenshots/wct.png", img_array)

    def render_game(self):
        # clear game screens
        self.touch_screen.refresh()
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
        self.instruction_loop()

        self.render_game()
        self.display_screen.instruction = "Match the card!"
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
                        else:
                            img_array = pg.surfarray.array3d(self.touch_screen.get_surface())
                            img_array = cv2.transpose(img_array)
                            img_array = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
                            cv2.imwrite("screenshots/wct.png", img_array)

        self.exit_sequence()


if __name__ == "__main__":
    os.chdir("/Users/benhoskings/Documents/Pycharm/Hero_Monitor")
    pg.init()
    card_game = CardGame(max_turns=3, size=(0.4 * 1024, 0.9 * 600))
    card_game.loop()
    print("Card game ran successfully")
