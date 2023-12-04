import random

colours = ['red', 'blue', 'green', 'yellow']
shapes = ['square', 'circle', 'triangle', 'diamond']

class Card:

    def __init__(self, deck, colour=None, shape=None, shape_count=None):
        self.colour = colour
        self.shape = shape
        self.shape_count = shape_count

        # if the attribute that is the current rule has been given, this card is set as 'correct':
        if (deck.rule == 'colour' and colour) or (deck.rule == 'shape' and shape) or (deck.rule == 'shape_count' and shape_count):
            self.correct = True
        else:
            self.correct = False

        # making sure that each card represents maximum and minimum of 1 quiz card attribute
        if not colour:
            self.colour = random.choice(list(set(colours) - {deck.quiz_colour}))
        if not shape:
            self.shape = random.choice(list(set(shapes) - {deck.quiz_shape}))
        if not shape_count:
            self.shape_count = random.choice(list(set([1, 2, 3]) - {deck.quiz_shape_count}))

class Deck:

    def __init__(self, rule):
        self.rule = rule
        self.generate_quiz_card()

        self.cards = []
        self.cards.append(Card(deck=self, shape=self.quiz_shape))
        self.cards.append(Card(deck=self, colour=self.quiz_colour))
        self.cards.append(Card(deck=self, shape_count=self.quiz_shape_count))

    def generate_quiz_card(self):
        self.quiz_shape = random.choice(shapes)
        self.quiz_colour = random.choice(colours)
        self.quiz_shape_count = random.randint(1, 3)
        self.quiz_card = Card(deck=self, shape=self.quiz_shape, colour=self.quiz_colour, shape_count=self.quiz_shape_count)
    
    def shuffle(self):
        random.shuffle(self.cards)
  