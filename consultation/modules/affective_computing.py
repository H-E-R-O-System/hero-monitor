import pygame as pg
from consultation.touch_screen import TouchScreen
from consultation.display_screen import DisplayScreen
from consultation.screen import Colours
import os


class AffectiveModule:
    def __init__(self, size=(1024, 600), parent=None):
        self.parent = parent
        if parent is not None:
            self.display_size = parent.display_size
            self.bottom_screen = parent.bottom_screen
            self.top_screen = parent.top_screen
        else:
            self.display_size = pg.Vector2(size)
            self.window = pg.display.set_mode((self.display_size.x, self.display_size.y * 2), pg.SRCALPHA)

            self.top_screen = self.window.subsurface(((0, 0), self.display_size))
            self.bottom_screen = self.window.subsurface((0, self.display_size.y), self.display_size)

        self.display_screen = DisplayScreen(self.display_size)
        self.touch_screen = TouchScreen(self.display_size)

        # Additional class properties
        self.thing1 = None
        self.thing2 = None

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
                    mouse_pos = pg.mouse.get_pos()
                    ...

                elif event.type == pg.QUIT:
                    # break the running loop
                    self.running = False

        self.exit_sequence()


if __name__ == "__main__":
    os.chdir("/Users/benhoskings/Documents/Pycharm/Hero_Monitor")

    pg.init()
    # Module Testing
    module_name = AffectiveModule()
    module_name.loop()
    print("Module run successfully")