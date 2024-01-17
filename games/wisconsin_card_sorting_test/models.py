import random
import pygame as pg
from consultation.screen import Colours

colours = ['red', 'blue', 'green', 'yellow']
shapes = ['square', 'circle', 'triangle', 'diamond']


class Card(pg.sprite.Sprite):
    def __init__(self, deck, size, colour=None, shape=None, shape_count=None):
        super().__init__()
        self.object_type = "card"
        self.size = pg.Vector2(size)
        self.rect = pg.Rect((0, 0), self.size)
        self.shape = shape
        self.shape_count = shape_count

        # if the attribute that is the current rule has been given, this card is set as 'correct':
        if (deck.rule == 'colour' and colour) or (deck.rule == 'shape' and shape) or (deck.rule == 'shape_count' and shape_count):
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
        if self.rect.collidepoint(pos):
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
                              colour=self.quiz_colour, shape_count=self.quiz_shape_count)

        self.cards = []
        self.cards.append(Card(deck=self, size=card_size, shape=self.quiz_shape))
        self.cards.append(Card(deck=self, size=card_size, colour=self.quiz_colour))
        self.cards.append(Card(deck=self, size=card_size, shape_count=self.quiz_shape_count))

        self.all_cards = [*self.cards.copy(), self.quiz_card]
    
    def shuffle(self):
        random.shuffle(self.cards)

    def update(self):
        self.all_cards = [*self.cards.copy(), self.quiz_card]
