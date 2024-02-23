import pygame as pg
from consultation.screen import Screen, Fonts, Colours
from consultation.display_screen import DisplayScreen
from consultation.touch_screen import TouchScreen, GameObjects, GameButton
import math


class Key(pg.sprite.Sprite):
    def __init__(self, letter, pos, size, colour=None):
        super().__init__()
        self.object_type = "card"
        self.screen = Screen(size=size, colour=Colours.white)
        self.size = pg.Vector2(size)
        self.screen.add_multiline_text(letter, ((0, 0), size), center_horizontal=True, center_vertical=True)

        self.image = self.screen.get_surface()
        self.rect = pg.Rect(pos, size)

        self.letter = letter

    def is_clicked(self, pos):
        if self.rect.collidepoint(pos):
            return True

    def click_return(self):
        return self.letter


import pygame as pg
from consultation.touch_screen import TouchScreen
from consultation.display_screen import DisplayScreen
from consultation.screen import Colours


class LoginScreen:
    def __init__(self, size=(1024, 600), parent=None):
        self.parent = parent
        if parent is not None:
            self.display_size = parent.display_size
            self.bottom_screen = parent.bottom_screen
            self.top_screen = parent.top_screen
        else:
            self.display_size = pg.Vector2(size)
            self.bottom_screen = pg.display.set_mode(self.display_size)
            self.top_screen = pg.display.set_mode(self.display_size)  # can set to None if not required

        self.display_screen = DisplayScreen(self.display_size)
        self.touch_screen = TouchScreen(self.display_size)

        # Additional class properties
        letters = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k",
                   "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v"]
        size = pg.Vector2(50, 50)

        option_count = 10
        card_width, h_gap = math.pow(option_count + 1, -1), math.pow(option_count + 1, -2)
        card_height, v_gap = math.pow(3, -1), math.pow(3, -2)

        self.option_coords = ([((idx * card_width + (idx + 1) * h_gap) * self.display_size.x,
                               0.3 * self.display_size.y)
                              for idx in range(option_count)] +
                              [((idx * card_width + (idx + 1) * h_gap) * self.display_size.x,
                                  0.6 * self.display_size.y)
                                 for idx in range(option_count)])

        # print(self.option_coords)

        self.keys = [GameButton(position=self.option_coords[idx], size=size, id=letters[idx], text=letters[idx])
                     for idx in range(option_count*2)]

        self.touch_screen.sprites = GameObjects(self.keys)

        self.running = False

    def update_display(self):
        self.top_screen.blit(self.display_screen.get_surface(), (0, 0))
        self.bottom_screen.blit(self.touch_screen.get_surface(), (0, 0))
        pg.display.flip()

    def entry_sequence(self):
        # pre-loop initialisation section
        # add everything needed to introduce your module and explain
        # what the users are expected to do (e.g. game rules, aim, etc.)
        self.running = True
        self.update_display()  # render graphics to main consult
        # add code below

    def do_something(self, ):
        # Do something useful
        ...

    def exit_sequence(self):
        # post-loop completion section
        # maybe add short thank you for completing the section?

        # only OPTIONAL and can leave blank
        ...

    def loop(self):
        self.entry_sequence()
        while self.running:
            for event in pg.event.get():
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_s:
                        # do something with key press
                        ...
                    elif event.key == pg.K_ESCAPE:
                        self.running = False

                elif event.type == pg.MOUSEBUTTONDOWN:
                    # do something with mouse click
                    button_id = self.touch_screen.click_test(self.parent.get_relative_mose_pos())
                    if button_id is not None:
                        print(button_id)

                elif event.type == pg.QUIT:
                    # break the running loop
                    self.running = False

        self.exit_sequence()


if __name__ == "__main__":
    pg.init()
    # Module Testing
    module_name = ModuleName()
    module_name.loop()
    print("Module run successfully")