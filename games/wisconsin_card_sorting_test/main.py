import pygame as pg
from models import *
from engine import *

class CardGame:

    def __init__(self):
        pg.init()
        self.running = True
        screen_size = (1024, 600)
        self.screen = pg.display.set_mode(screen_size)
        pg.display.set_caption('Wisconsin Card Sorting Test')
        self.engine = CardGameEngine()

        self.white = (255, 255, 255)
        grey = (192, 192, 192)
        self.black = (0, 0, 0)
        self.colours = {'red': (181, 67, 67),
                'blue': (67, 113, 181),
                'green': (69, 181, 67),
                'yellow': (252, 198, 3)}

        card_width, card_height = 150, 200
        white_fill = pg.Surface((card_width, card_height))
        white_fill.fill(self.white)
        self.card_surface_template = pg.Surface((card_width + 14, card_height + 14))
        self.card_surface_template.fill(grey)
        self.card_surface_template.blit(white_fill, (7, 7))

    def render_game(self):
        self.screen.fill(self.white)

        self.blit_card(self.card_surface_template.copy(), self.engine.deck.quiz_card, (450, 50))

        option_coords = [(150, 325), (450, 325), (750, 325)]

        for i in range(3):
            self.blit_card(self.card_surface_template.copy(), self.engine.deck.cards[i], option_coords[i])


    def blit_card(self, card_surface, card, coords):
        x, y = coords
        colour = self.colours[card.colour]
        shape = card.shape
        shape_count = card.shape_count
        
        self.draw_shapes(card_surface, colour, shape, shape_count)

        card.rect = card_surface.get_rect(topleft=(x, y))
        self.screen.blit(card_surface, (x, y))

    def draw_shapes(self, card_surface, colour, shape, count):
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
                
    def entry_sequence(self):
        pass

    def exit_sequence(self):
        font = pg.font.Font(None, 36)
        self.screen.fill((255, 255, 255))
        text_surface = font.render('Game Completed!', True, (0, 0, 0))  # Green text
        text_rect = text_surface.get_rect(center=(512, 250))
        self.screen.blit(text_surface, text_rect)
        text_surface = font.render('Score: ' + str(self.engine.score), True, (0, 0, 0))  # Green text
        text_rect = text_surface.get_rect(center=(512, 300))
        self.screen.blit(text_surface, text_rect)
        pg.display.flip() 

    def loop(self):
        game_over = False
        while self.running:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.running = False
                elif game_over:
                    self.exit_sequence()
                elif event.type == pg.MOUSEBUTTONDOWN:
                    pos = pg.mouse.get_pos()
                    for card in self.engine.deck.cards:

                        if card.rect.collidepoint(pos):
                            if card.correct:
                                self.engine.correct_selection(self.screen)
                            else:
                                self.engine.incorrect_selection(self.screen)
                            
                            self.engine.turns += 1
                            if self.engine.turns == 10:
                                game_over = True
                            else:
                                self.engine.deal()

            if not game_over:
                self.render_game()

            pg.display.update()

if __name__ == "__main__":
    card_game = CardGame()
    card_game.loop()
    print("Card game ran successfully")