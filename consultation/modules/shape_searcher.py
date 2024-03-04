import os
import random
import time

import numpy as np
import pandas as pd
import pygame as pg

from consultation.display_screen import DisplayScreen
from consultation.screen import Colours
from consultation.touch_screen import TouchScreen, GameObjects, GameButton
from consultation.utils import take_screenshot

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
    def __init__(self, position, size, colour):
        super().__init__()
        self.object_type = "circle"
        surf_size = pg.Vector2(size, size)
        self.image = pg.Surface(surf_size, pg.SRCALPHA)
        pg.draw.circle(self.image, colour.value, surf_size / 2, size / 2)
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
    def __init__(self, size=(1024, 600), parent=None, auto_run=False):
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

        self.display_screen.instruction = None

        self.touch_screen = TouchScreen(self.display_size)
        self.button_size = pg.Vector2(self.display_size.x * 0.45, 100)
        button_pad = pg.Vector2(self.touch_screen.size.y, self.touch_screen.size.y) * 0.05
        self.same_button = GameButton(position=(button_pad.x,
                                                self.touch_screen.size.y - button_pad.y - self.button_size.y),
                                      size=self.button_size, id=1, text="Same")
        self.different_button = GameButton(position=(self.touch_screen.size.x - button_pad.x - self.button_size.x,
                                                     self.touch_screen.size.y - button_pad.y - self.button_size.y),
                                           size=self.button_size, id=0, text="Different")

        self.shape_size = pg.Vector2(80, 80)
        self.match = None

        self.turns = 0

        self.scores = [0, 0, 0]

        self.question_counts = [10, 8, 8]

        self.answer_times = []
        self.start_time = None

        self.question_types = (["perception" for _ in range(self.question_counts[0])] +
                               ["shape" for _ in range(self.question_counts[1])] +
                               ["colour" for _ in range(self.question_counts[2])])

        # initialise module
        self.running = False
        self.auto_run = auto_run

    def instruction_loop(self, question):
        if self.auto_run:
            return

        temp_instruction = self.display_screen.instruction
        self.display_screen.state = 1
        self.display_screen.refresh()
        self.display_screen.instruction = None

        button_rect = pg.Rect((self.display_size - pg.Vector2(300, 200))/2, (300, 200))
        start_button = GameButton(position=button_rect.topleft, size=button_rect.size, text="START", id=1)
        self.touch_screen.sprites = GameObjects([start_button])
        info_rect = pg.Rect(0.3 * self.display_size.x, 0, 0.7 * self.display_size.x, 0.8 * self.display_size.y)
        pg.draw.rect(self.display_screen.surface, Colours.white.value,
                     info_rect)

        self.display_screen.add_multiline_text("Match the Shapes!", rect=info_rect.scale_by(0.9, 0.9),
                                               font_size=50)

        if question == "perception":
            info_text = (
                "You will see three coloured shapes located above and below a black line. " +
                "Your task is to say whether the shapes that you see above the line are the same as the shapes below the line.")
            self.display_screen.add_multiline_text(
                rect=info_rect.scale_by(0.9, 0.9), text=info_text,
                center_vertical=True)
        else:
            info_text = ("You will now have to try and remember a set of coloured shapes. You will be shown two or three " +
                "shapes, which will then disappear after a short amount of time. A second set of shapes will then appear, " +
                "and your task is to identify if the two sets are the same or different. Sets are considered the " +
                "same if each shape and colour matches.")
            # info_text=""
            self.display_screen.add_multiline_text(
                rect=info_rect.scale_by(0.9, 0.9), text=info_text,
                center_vertical=True)

        self.update_display()
        if self.parent:
            self.parent.speak_text(
                info_text, visual=True, display_screen=self.display_screen, touch_screen=self.touch_screen)

        self.update_display()
        wait = True
        while wait:
            for event in pg.event.get():
                if event.type == pg.MOUSEBUTTONDOWN:
                    pos = pg.Vector2(pg.mouse.get_pos()) - pg.Vector2(0, self.display_size.y)

                    selection = self.touch_screen.click_test(pos)
                    if selection is not None:
                        wait = False

                elif event.type == pg.KEYDOWN:
                    if event.key == pg.K_w:
                        if self.parent:
                            take_screenshot(self.parent.window)
                        else:
                            take_screenshot(self.window, "Shape_match")

        self.touch_screen.kill_sprites()
        self.display_screen.state = 0
        self.display_screen.refresh()
        self.display_screen.instruction = temp_instruction
        print(self.display_screen.instruction)
        self.update_display()

    def update_display(self):

        self.top_screen.blit(self.display_screen.get_surface(), (0, 0))
        self.bottom_screen.blit(self.touch_screen.get_surface(), (0, 0))
        pg.display.flip()

    def entry_sequence(self):
        # pre-loop initialisation section
        # add everything needed to introduce your module and explain
        # what the users are expected to do (e.g. game rules, aim, etc.)

        # only OPTIONAL and can leave blank
        self.update_display()
        if self.parent:
            self.parent.speak_text("your next set of tasks will all involve matching sets of shapes",
                                   display_screen=self.display_screen, touch_screen=self.touch_screen)
        self.display_screen.instruction = "Match the sets!"
        self.instruction_loop(question="perception")

        self.perception_question()
        self.touch_screen.sprites = GameObjects([self.same_button, self.different_button])
        self.update_display()
        self.running = True
        self.start_time = time.monotonic()

    def check_ok(self, pos, existing):
        for point in existing:
            invalid = pg.Rect((point.x - self.shape_size.x, point.y - self.shape_size.y),
                              self.shape_size * 2).scale_by(1.1, 1.1)

            if invalid.collidepoint(pos):
                return False

        else:
            return True

    def generate_symbol_set(self, area, shape_count, scene_shapes=None, colours=None):
        area = area.copy()
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

        place_area = pg.Rect((0, 0), self.touch_screen.size).scale_by(0.95, 0.7)
        place_area.topleft -= pg.Vector2(0, self.touch_screen.size.y * 0.1)

        # pg.draw.rect(self.touch_screen.surface, Colours.red.value, place_area)

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

    def binding_question(self, colour=True):
        self.touch_screen.refresh()
        self.display_screen.instruction = "Do the sets match?"
        self.touch_screen.kill_sprites()
        place_area = pg.Rect((0, 0), self.touch_screen.size).scale_by(0.7, 0.7)
        place_area.topleft -= pg.Vector2(0, self.touch_screen.size.y * 0.1)

        shape_count = np.random.randint(2, 4)

        if not colour:
            colours = [Colours.hero_blue for _ in range(shape_count)]
        else:
            colours = None

        symbol_set_1, scene_shapes, scene_colours = self.generate_symbol_set(place_area, shape_count, colours=colours)
        self.match = np.random.randint(0, 2)

        symbol_set_2, _, _ = self.generate_symbol_set(place_area, shape_count, colours=scene_colours,
                                                      scene_shapes=scene_shapes)

        for symbol, pos in symbol_set_1:
            self.touch_screen.add_surf(symbol, pos)

        self.update_display()
        if not self.auto_run:
            time.sleep(2)  # Time to see shapes

        self.touch_screen.refresh()
        # pg.draw.rect(self.touch_screen.surface, Colours.red.value, place_area)
        self.update_display()
        if not self.auto_run:
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
        ...

    def process_selection(self, selection):
        self.answer_times.append(self.start_time - time.monotonic())

        if selection == self.match:
            if self.question_types[self.turns] == "perception":
                self.scores[0] += 1
            elif self.question_types[self.turns] == "shape":
                self.scores[1] += 1
            else:
                self.scores[2] += 1

        self.turns += 1
        if self.turns == sum(self.question_counts):
            # stop test
            self.running = False
        elif self.turns == self.question_counts[0] and self.scores[0] < 8:
            # fail test
            print("Score too low to continue")
            self.running = False
        else:
            # Update for next question
            if self.turns == 10:
                if self.parent:
                    self.display_screen.refresh()
                    self.touch_screen.kill_sprites()
                    self.touch_screen.refresh()
                    self.display_screen.instruction = None
                    self.update_display()

                    self.parent.speak_text("Well done, we are now moving onto the second task",
                                           display_screen=self.display_screen, touch_screen=self.touch_screen)
                    self.display_screen.instruction = "Do the sets match?"

                self.touch_screen.refresh()
                self.instruction_loop("shape")
                self.display_screen.refresh()

            if self.question_types[self.turns] == "perception":
                self.perception_question()
            elif self.question_types[self.turns] == "shape":
                self.binding_question(colour=False)
            else:
                self.binding_question()

        self.start_time = time.monotonic()

    def loop(self):
        self.entry_sequence()
        while self.running:
            if self.auto_run:
                if self.question_types[self.turns] == "perception":
                    weights = [9, 1]
                elif self.question_types[self.turns] == "shape":
                    weights = [65, 35]
                else:
                    weights = [8, 2]

                if self.match:
                    weights.reverse()

                selection = random.choices([0, 1], weights=weights, k=1)[0]
                self.process_selection(selection)

                # if self.turns == 9:
                #     self.auto_run = False
            else:
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
                        pos = pg.Vector2(pg.mouse.get_pos()) - pg.Vector2(0, self.display_size.y)

                        selection = self.touch_screen.click_test(pos)

                        if selection is not None:
                            self.process_selection(selection)

                        pg.event.clear()

                    elif event.type == pg.QUIT:
                        # break the running loop
                        self.running = False

        self.exit_sequence()


if __name__ == "__main__":
    os.chdir("/Users/benhoskings/Documents/Pycharm/Hero_Monitor")
    pg.init()
    pg.event.pump()
    # Module Testing
    shape_searcher = ShapeSearcher(auto_run=True)
    shape_searcher.loop()
    print(f"Score: {sum(shape_searcher.scores)}/{sum(shape_searcher.question_counts)}")
    print("Module run successfully")
