import math
import os
import random
import time

import cv2
import pygame as pg
import numpy as np

from consultation.display_screen import DisplayScreen
from consultation.screen import Colours, BlitLocation
from consultation.touch_screen import GameObjects, TouchScreen, GameButton
from consultation.utils import take_screenshot

colours = ['red', 'blue', 'green', 'yellow']
shapes = ['square', 'circle', 'triangle', 'diamond']
rules = ['colour', 'shape', 'shape_count']


class Card(pg.sprite.Sprite):
    def __init__(self, rule, value, size, id, colour=None, shape=None, shape_count=None, quiz_card=False):
        super().__init__()
        self.object_type = "card"
        self.size = pg.Vector2(size)
        self.rect = pg.Rect((0, 0), self.size)
        self.shape = shape
        self.colour_name = colour
        self.shape_count = shape_count
        self.quiz_card = quiz_card
        self.id = id

        self.colour = Colours[colour]

        # if the attribute that is the current rule has been given, this card is set as 'correct':
        if (rule == 'colour' and colour == value) or (rule == 'shape' and shape == value) or (
           rule == 'shape_count' and shape_count == value):
            self.correct = True
        else:
            self.correct = False

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
        return self.correct, self.id


class Deck:
    def __init__(self, rule, card_size):
        self.rule = rule
        self.quiz_shape = random.choice(shapes)
        self.quiz_colour = random.choice(colours)
        self.quiz_shape_count = random.randint(1, 3)

        if rule == "shape":
            quiz_val = self.quiz_shape
        elif rule == "colour":
            quiz_val = self.quiz_colour
        else:
            quiz_val = self.quiz_shape_count

        self.cards = []
        card_colours = np.random.permutation([colour for colour in colours if colour != self.quiz_colour])
        card_shapes = np.random.permutation([shape for shape in shapes if shape != self.quiz_shape])
        shape_counts = np.random.permutation([count for count in range(1, 4) if count != self.quiz_shape_count])

        self.cards.append(Card(rule=rule, value=quiz_val, size=card_size, id =0, colour=self.quiz_colour,
                               shape=card_shapes[0], shape_count=shape_counts[0]))
        self.cards.append(Card(rule=rule, value=quiz_val, size=card_size, id =1, colour=card_colours[0],
                               shape=self.quiz_shape, shape_count=shape_counts[1]))
        self.cards.append(Card(rule=rule, value=quiz_val, size=card_size, id=2, colour=card_colours[1],
                               shape=card_shapes[1], shape_count=self.quiz_shape_count))

        self.quiz_card = Card(rule=rule, value=quiz_val, size=card_size, id=3, shape=self.quiz_shape,
                              colour=self.quiz_colour, shape_count=self.quiz_shape_count, quiz_card=True)

        self.all_cards = [*self.cards.copy(), self.quiz_card]

    def shuffle(self):
        random.shuffle(self.cards)

    def update(self):
        self.all_cards = [*self.cards.copy(), self.quiz_card]


class CardGameEngine:
    def __init__(self, quiz_coord, option_coords, card_size=(164, 214)):
        self.rule = random.choice(rules)
        self.score = 0
        self.turns = 0
        self.rule_turns = 0
        self.card_size = card_size
        self.quiz_coord = quiz_coord
        self.option_coords = option_coords
        self.deck = None
        self.new_rule_ids = []
        self.answers = []

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

    def check_update(self):
        if self.rule_turns > 4:
            if random.randint(1, 10) <= 6:
                self.rule = random.choice([rule for rule in rules if rule != self.rule])
                # print(f"new rule: {self.rule}")
                self.rule_turns = 0
                self.new_rule_ids.append(self.turns)


class CardGame:

    def __init__(self, size=(1024, 600), max_turns=10, parent=None, auto_run=False):
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

        self.display_screen.instruction = "Match the card!"
        self.touch_screen = TouchScreen(self.display_size, colour=Colours.white.value)

        self.running = False

        # Card positioning in the display_screen. The positions specify the center of the card.
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
        self.auto_run = auto_run

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
                                               font_size=50)

        self.display_screen.add_multiline_text(
            rect=info_rect.scale_by(0.9, 0.9), text=
            "n this game you must match the cards based on the pictures on the cards to the 3 cards at the bottom of"
            " the screen. Each card has a different colour, number and shape. There is a rule for matching the cards "
            "but I cannot tell you what the rule is but I can tell you if you are correct. Finally the rule will "
            "change during the game and you will have to figure out the new rule.",
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
        if self.parent:
            self.parent.speak_text("Match the card", visual=True,
                                   display_screen=self.display_screen, touch_screen=self.touch_screen)

        wait = True
        while wait:
            for event in pg.event.get():
                if event.type == pg.MOUSEBUTTONDOWN:
                    if self.parent:
                        pos = self.parent.get_relative_mose_pos()
                    else:
                        pos = pg.Vector2(pg.mouse.get_pos()) - pg.Vector2(0, self.display_size.y)

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

    def display_message(self, answer, card_id):
        if self.auto_run:
            return

        card = self.touch_screen.get_object(card_id)
        card: Card

        self.display_screen.refresh()
        self.display_screen.instruction = None
        if answer:
            self.display_screen.speech_text = "Correct"
            pg.draw.rect(card.image, Colours.green.value, card.image.get_rect(), width=10)
        else:
            self.display_screen.speech_text = "Incorrect"
            pg.draw.rect(card.image, Colours.red.value, card.image.get_rect(), width=10)

        if self.parent:
            self.parent.speak_text(
                self.display_screen.speech_text, display_screen=self.display_screen, touch_screen=self.touch_screen)

        self.update_displays()

        self.touch_screen.kill_sprites()
        time.sleep(0.5)

        self.display_screen.speech_text = None
        self.display_screen.instruction = "Select the card you think matches"
        self.display_screen.refresh()
        # self.display_screen.state = 0

    def update_displays(self):
        self.top_screen.blit(self.display_screen.get_surface(), (0, 0))

        self.bottom_screen.blit(self.touch_screen.get_surface(), (0, 0))
        pg.display.flip()

    def process_selection(self, selection, card_id):
        self.display_message(selection, card_id)

        if selection:
            self.engine.score += 1

        self.engine.rule_turns += 1
        self.engine.turns += 1

        self.engine.answers.append(selection)

        if self.engine.turns == self.max_turns:
            self.running = False
        else:
            self.engine.check_update()
            self.engine.deal()
            self.render_game()

    def entry_sequence(self):
        if not self.auto_run:
            self.instruction_loop()

        self.render_game()
        self.display_screen.instruction = "Match the card!"

        self.display_screen.state = 0
        self.display_screen.refresh()
        self.render_game()

        self.running = True

    def exit_sequence(self):
        ...
        # return [self.engine.answers, self.engine.new_rule_ids]

    def loop(self):
        self.entry_sequence()
        while self.running:
            if self.auto_run:
                card_idx = random.randint(0, 2)
                card = self.touch_screen.get_object(card_idx)
                selection, card_id = card.correct, card.id
                self.process_selection(selection, card_id)

            else:
                for event in pg.event.get():
                    if event.type == pg.QUIT:
                        self.running = False

                    elif event.type == pg.KEYDOWN:
                        if event.key == pg.K_s:
                            if self.parent:
                                take_screenshot(self.parent.window)
                            else:
                                take_screenshot(self.window, "wisconsin_card_test")

                    elif event.type == pg.MOUSEBUTTONDOWN:
                        if self.parent:
                            pos = self.parent.get_relative_mose_pos()
                        else:
                            pos = pg.Vector2(pg.mouse.get_pos()) - pg.Vector2(0, self.display_size.y)

                        output = self.touch_screen.click_test(pos)
                        if output is not None:
                            selection, card_id = output
                        else:
                            selection, card_id = None, None

                        if selection is not None:
                            self.process_selection(selection, card_id)



        self.exit_sequence()


if __name__ == "__main__":
    os.chdir("/Users/benhoskings/Documents/Pycharm/Hero_Monitor")
    pg.init()
    pg.event.pump()
    card_game = CardGame(max_turns=20, auto_run=False)
    card_game.loop()
    print("Card game ran successfully")
