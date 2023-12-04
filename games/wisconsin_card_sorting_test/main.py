import pygame as pg
from models import *
from engine import *

pg.init()
screen_size = (1024, 600)
screen = pg.display.set_mode(screen_size)
pg.display.set_caption('Wisconsin Card Sorting Test')

gameEngine = CardGameEngine()

white = (255, 255, 255)
grey = (192, 192, 192)
black = (0, 0, 0)
colours = {'red': (181, 67, 67),
           'blue': (67, 113, 181),
           'green': (69, 181, 67),
           'yellow': (252, 198, 3)}

card_width, card_height = 150, 200
white_fill = pg.Surface((card_width, card_height))
white_fill.fill(white)

card_surface_template = pg.Surface((card_width + 14, card_height + 14))
card_surface_template.fill(grey)
card_surface_template.blit(white_fill, (7, 7))

def render_game(window):
    window.fill(white)

    # helpful info to see when testing:
    # font = pg.font.Font(None, 36)
    # text = font.render('Rule: ' + gameEngine.deck.rule, True, (0, 0, 0))
    # window.blit(text, (0, 0))
    # text = font.render('Score: ' + str(gameEngine.score), True, (0, 0, 0))
    # window.blit(text, (0, 20))
    # text = font.render('Turns: ' + str(gameEngine.turns), True, (0, 0, 0))
    # window.blit(text, (0, 40))

    blit_card(window, card_surface_template.copy(), gameEngine.deck.quiz_card, (450, 50))

    option_coords = [(150, 325), (450, 325), (750, 325)]

    for i in range(3):
        blit_card(window, card_surface_template.copy(), gameEngine.deck.cards[i], option_coords[i])


def blit_card(window, card_surface, card, coords):

    x, y = coords
    colour = colours[card.colour]
    shape = card.shape
    shape_count = card.shape_count
    
    draw_shapes(card_surface, colour, shape, shape_count)

    card.rect = card_surface.get_rect(topleft=(x, y))
    window.blit(card_surface, (x, y))

def draw_shapes(card_surface, colour, shape, count):
    card_width, card_height = card_surface.get_size()

    shape_size = min(card_width, card_height) // 5
    spacing = (card_width - (count * shape_size)) // (count + 1)

    for i in range(count):

        x = spacing + i * (spacing + shape_size)
        y = card_height // 2

        if shape == 'triangle':
            pg.draw.polygon(card_surface, colour, [(x, y - shape_size // 2),
                                                      (x + shape_size, y - shape_size // 2),
                                                      (x + shape_size // 2, y + shape_size // 2)])
        elif shape == 'circle':
            pg.draw.circle(card_surface, colour, (x + shape_size // 2, y), shape_size // 2)
        elif shape == 'square':
            pg.draw.rect(card_surface, colour, (x, y - shape_size // 2, shape_size, shape_size))
        elif shape == 'diamond':
            pg.draw.polygon(card_surface, colour, [(x, y),
                                                      (x + shape_size // 2, y - shape_size // 2),
                                                      (x + shape_size, y),
                                                      (x + shape_size // 2, y + shape_size // 2)])

run = True
game_over = False
while run:
    key = None
    for event in pg.event.get():
        if event.type == pg.QUIT:
            run = False
        elif game_over:
            gameEngine.final_screen(screen)
        elif event.type == pg.MOUSEBUTTONDOWN:
            pos = pg.mouse.get_pos()
            for card in gameEngine.deck.cards:

                if card.rect.collidepoint(pos):
                    if card.correct:
                        gameEngine.correct_selection(screen)
                    else:
                        gameEngine.incorrect_selection(screen)
                    
                    gameEngine.turns += 1
                    if gameEngine.turns == 10:
                        game_over = True
                    else:
                        gameEngine.deal()

    if not game_over:
        render_game(screen)

    pg.display.update()
