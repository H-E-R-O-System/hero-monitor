import os
import time

import numpy as np
import pandas as pd
import pygame as pg

from consultation.display_screen import DisplayScreen
from consultation.screen import Colours
from consultation.touch_screen import TouchScreen, GameObjects, GameButton

rocket = [(4, 0), (8, 4), (5, 8), (4, 5), (3, 8), (0, 4)]
lightning_1 = [(5, 0), (5, 3), (8, 3), (3, 8), (3, 5), (0, 5)]
lightning_2 = [(4, 0), (4, 2.5), (8, 5.5), (4, 8), (4, 5.5), (0, 2.5)]
arrow_1 = [(1.5, 0), (4, 0), (8, 4), (3.25, 8), (0, 8), (5, 3.5)]
arrow_2 = [(0, 0), (7, 5), (7, 8), (3, 5), (3, 8), (0, 8)]
gem = [(5, 0), (8, 2), (8, 5), (3, 8), (0, 6), (0, 3)]
staple = [(1, 0), (7, 0), (7, 8), (1, 8), (3.5, 5.5), (3.5, 2.5)]

shapes = {"rocket": rocket, "lightning_1": lightning_1,
          "arrow_1": arrow_1, "lightning_2": lightning_2,
          "arrow_2": arrow_2, "gem": gem, "staple": staple}

shape_colours = [Colours.red, Colours.blue, Colours.green, Colours.yellow, Colours.shadow]


class Circle(pg.sprite.Sprite):
    def __init__(self, position, size, colour, text=None, label=None):
        super().__init__()
        self.object_type = "circle"
        surf_size = pg.Vector2(size, size)
        self.image = pg.Surface(surf_size, pg.SRCALPHA)
        pg.draw.circle(self.image, colour.value, surf_size/2, size/2)
        self.rect = pg.Rect(position, surf_size)

    def is_clicked(self, pos):
        if self.rect.collidepoint(pos):
            return True
        else:
            return False

    def click_return(self):
        return True


def create_shape_surf(name, scale, colour):
    shape_surf = pg.Surface((8 * scale, 8 * scale), pg.SRCALPHA)
    shape_coords = [(coord[0] * scale, coord[1] * scale) for coord in shapes[name]]
    pg.draw.polygon(shape_surf, colour.value, shape_coords)
    return shape_surf


class ShapeSearcher:
    def __init__(self, size=(1024, 600), max_turns=10, parent=None):
        self.parent = parent
        if parent is not None:
            self.display_size = parent.display_size
            self.bottom_screen = parent.bottom_screen
            self.top_screen = parent.top_screen

            self.display_screen = DisplayScreen(self.display_size, avatar=parent.avatar)
        else:
            self.display_size = pg.Vector2(size)
            self.bottom_screen = pg.display.set_mode(self.display_size)
            self.top_screen = pg.display.set_mode(self.display_size)  # can set to None if not required

            self.display_screen = DisplayScreen(self.display_size)

        self.display_screen.instruction = None
        if parent:
            self.display_screen.avatar = parent.display_screen.avatar

        self.touch_screen = TouchScreen(self.display_size)
        self.button_size = pg.Vector2(120, 100)
        button_pad = pg.Vector2(self.touch_screen.size.y, self.touch_screen.size.y) * 0.05
        self.same_button = GameButton(position=(button_pad.x,
                                                self.touch_screen.size.y - button_pad.y - self.button_size.y),
                                      size=self.button_size, id=1, text="Same")
        self.different_button = GameButton(position=(self.touch_screen.size.x - button_pad.x - self.button_size.x,
                                                     self.touch_screen.size.y - button_pad.y - self.button_size.y),
                                           size=self.button_size, id=0, text="Different")

        self.touch_screen.sprites = GameObjects([self.same_button, self.different_button])

        self.shape_size = pg.Vector2(80, 80)
        self.match = None

        self.score, self.turns, self.max_turns = 0, 0, max_turns

        self.question_type = "speed"

        # initialise module
        self.running = False

    def update_display(self):
        if self.parent:
            self.display_screen.refresh()
            self.top_screen.blit(self.display_screen.get_surface(), (0, 0))
        self.bottom_screen.blit(self.touch_screen.get_surface(), (0, 0))
        pg.display.flip()

    def entry_sequence(self):
        # pre-loop initialisation section
        # add everything needed to introduce your module and explain
        # what the users are expected to do (e.g. game rules, aim, etc.)

        # only OPTIONAL and can leave blank
        if self.question_type == "perception":
            self.perception_question()
        elif self.question_type == "speed":
            self.speed_question()
        else:
            self.binding_question()

        self.update_display()
        self.running = True

    def check_ok(self, pos, existing):
        for point in existing:
            invalid = pg.Rect((point.x - self.shape_size.x, point.y - self.shape_size.y),
                              self.shape_size * 2).scale_by(1.1, 1.1)

            if invalid.collidepoint(pos):
                return False

        else:
            return True

    def generate_symbol_set(self, area, shape_count, scene_shapes=None, colours=None):
        area.size -= self.shape_size
        if colours is None:
            # Select random colours form group
            colours = pd.Series(shape_colours)[np.random.permutation(len(shape_colours))[range(shape_count)]]
        if scene_shapes is None:
            # select random_shapes form group
            scene_shapes = pd.Series(shapes.keys())[np.random.permutation(len(shapes))[range(shape_count)]]
        elif not self.match:
            # select shapes for set. The while loop ensures that the sets are not the same by chance
            new_shapes = pd.Series(shapes.keys())[np.random.permutation(len(shapes))[range(shape_count)]]
            while all(x in new_shapes for x in scene_shapes):
                new_shapes = pd.Series(shapes.keys())[np.random.permutation(len(shapes))[range(shape_count)]]
            scene_shapes = new_shapes

        positions = []
        for idx in range(shape_count):
            test_pos = (area.topleft +
                        pg.Vector2(np.random.randint(0, area.width + 1),
                                   np.random.randint(0, area.height + 1)))

            while not self.check_ok(test_pos, positions):
                test_pos = (area.topleft +
                            pg.Vector2(np.random.randint(0, area.width + 1),
                                       np.random.randint(0, area.height + 1)))

            positions.append(test_pos)

        return [(create_shape_surf(name, 10, colour), position) for
                name, colour, position in zip(scene_shapes, colours, positions)], scene_shapes, colours

    def perception_question(self):
        self.touch_screen.refresh()

        self.display_screen.instruction = "Do the sets match?"

        place_area = pg.Rect((0, 0), self.touch_screen.size).scale_by(0.7, 0.9)

        place_area_top = pg.Rect(place_area.topleft, (place_area.width, place_area.height / 2)).scale_by(0.9, 0.9)
        place_area_bottom = pg.Rect(place_area.midleft, (place_area.width, place_area.height / 2)).scale_by(0.9, 0.9)

        symbol_set_1, scene_shapes, scene_colours = self.generate_symbol_set(place_area_top, 3)

        self.match = np.random.randint(0, 2)

        symbol_set_2, _, _ = self.generate_symbol_set(place_area_bottom, 3, colours=scene_colours,
                                                      scene_shapes=scene_shapes)

        pg.draw.line(self.touch_screen.surface, Colours.black.value, place_area.midleft, place_area.midright, width=5)

        for symbol, pos in symbol_set_1:
            self.touch_screen.add_surf(symbol, pos)

        for symbol, pos in symbol_set_2:
            self.touch_screen.add_surf(symbol, pos)

        self.update_display()

    def binding_question(self):
        self.touch_screen.refresh()
        self.display_screen.instruction = "Do the sets match?"
        self.touch_screen.kill_sprites()

        place_area = pg.Rect((0, 0), self.touch_screen.size).scale_by(0.6, 0.6)

        shape_count = np.random.randint(2, 4)

        symbol_set_1, scene_shapes, scene_colours = self.generate_symbol_set(place_area, shape_count)

        self.match = np.random.randint(0, 2)

        symbol_set_2, _, _ = self.generate_symbol_set(place_area, shape_count, colours=scene_colours,
                                                      scene_shapes=scene_shapes)

        for symbol, pos in symbol_set_1:
            self.touch_screen.add_surf(symbol, pos)

        self.update_display()
        time.sleep(2)  # Time to see shapes

        self.touch_screen.refresh()
        self.update_display()
        time.sleep(2)  # Time invisible for

        for symbol, pos in symbol_set_2:
            self.touch_screen.add_surf(symbol, pos)
        self.touch_screen.sprites = GameObjects([self.same_button, self.different_button])
        self.update_display()

    def speed_question(self):
        self.touch_screen.refresh()
        self.touch_screen.kill_sprites()
        self.display_screen.instruction = "Touch the dot!"

        size = np.random.randint(20, 51)
        place_area = pg.Rect((0, 0), self.touch_screen.size).scale_by(0.6, 0.6)
        place_area.size -= pg.Vector2(size, size)

        pos = (place_area.topleft +
                    pg.Vector2(np.random.randint(0, place_area.width + 1),
                               np.random.randint(0, place_area.height + 1)))

        circle = Circle(pos, size, Colours.red)

        self.touch_screen.sprites = GameObjects([circle])
        self.update_display()

    def exit_sequence(self):
        # post-loop completion section
        print(f"Score: {self.score}/{self.max_turns}")

    def loop(self):
        self.entry_sequence()
        while self.running:
            for event in pg.event.get():
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_w:
                        if self.parent:
                            self.parent.take_screenshot(filename="shape_searcher")
                            ...
                        elif event.key == pg.K_ESCAPE:
                            self.running = False

                elif event.type == pg.MOUSEBUTTONDOWN:
                    # do something with mouse click
                    if self.parent:
                        pos = self.parent.get_relative_mose_pos()
                    else:
                        pos = pg.mouse.get_pos()

                    selection = self.touch_screen.click_test(pos)

                    if selection is not None:
                        if self.question_type == "speed":
                            print("selected")
                            self.touch_screen.kill_sprites()  # Remove circle from touch screen
                        else:
                            if (selection and self.match) or (not selection and not self.match):
                                self.score += 1
                                print("Correct")
                            else:
                                print("Incorrect")

                        self.turns += 1
                        if self.turns == self.max_turns:
                            self.running = False
                        else:
                            if self.turns >= 2*((self.max_turns-1) / 3):
                                self.question_type = "perception"
                            elif self.turns >= ((self.max_turns-1) / 3):
                                self.question_type = "binding"

                            # Update for next question
                            if self.question_type == "perception":
                                self.touch_screen.sprites = GameObjects([self.same_button, self.different_button])
                                self.perception_question()
                            elif self.question_type == "speed":
                                self.touch_screen.kill_sprites()
                                self.speed_question()
                            else:
                                self.touch_screen.sprites = GameObjects([self.same_button, self.different_button])
                                self.binding_question()

                elif event.type == pg.QUIT:
                    # break the running loop
                    self.running = False

        self.exit_sequence()


if __name__ == "__main__":
    os.chdir("/Users/benhoskings/Documents/Pycharm/Hero_Monitor")
    pg.init()
    # Module Testing
    shape_searcher = ShapeSearcher(max_turns=10)
    shape_searcher.loop()
    print("Module run successfully")
