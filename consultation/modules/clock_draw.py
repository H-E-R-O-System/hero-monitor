import pygame as pg
import numpy as np
import os
import datetime
from random import randrange
import timeit

from consultation.touch_screen import TouchScreen, GameObjects, GameButton
from consultation.display_screen import DisplayScreen
from consultation.screen import Colours, BlitLocation

from shapely import geometry

hour_hand = [(1, 0), (2, 1), (2, 8), (0, 8), (0, 1)]
minute_hand = [(1, 0), (2, 1), (2, 8), (0, 8), (0, 1)]


def create_shape_surf(points, scale, colour):
    shape_surf = pg.Surface((8 * scale, 8 * scale), pg.SRCALPHA)
    shape_coords = [(coord[0] * scale, coord[1] * scale) for coord in points]
    pg.draw.polygon(shape_surf, colour.value, shape_coords)
    return shape_surf


class ClockHand(pg.sprite.Sprite):
    def __init__(self, id, clock_radius=200, hand_radius=150):
        super().__init__()
        self.id = id
        self.object_type = "clock_hand"

        self.image = None
        self.clock_radius = clock_radius
        self.hand_radius = hand_radius
        self.collide_region = None
        self.endpoint = None
        self.update_image((0, -1))

        line = geometry.LineString([(200, 200), (300, 200), (300, 300), (200, 300)])
        self.square = geometry.Polygon(line)

    def update_image(self, pos):
        unit_vec = pg.Vector2(pos) / np.linalg.norm(pos)
        angle_1 = 140
        theta_1 = np.radians(angle_1)

        rotMatrix_1 = np.array([[np.cos(theta_1), -np.sin(theta_1)], [np.sin(theta_1), np.cos(theta_1)]])
        rotMatrix_2 = rotMatrix_1.transpose()

        direction = np.reshape(unit_vec, (2, 1))

        head_1, head_2 = np.matmul(rotMatrix_1, direction), np.matmul(rotMatrix_2, direction)

        direction_vec = unit_vec * self.hand_radius + pg.Vector2(self.clock_radius, self.clock_radius)
        head_1 = pg.Vector2(head_1[0, 0], head_1[1, 0]) * (self.hand_radius / 15) + direction_vec
        head_2 = pg.Vector2(head_2[0, 0], head_2[1, 0]) * (self.hand_radius / 15) + direction_vec

        self.image = pg.Surface((self.clock_radius * 2, self.clock_radius * 2), pg.SRCALPHA)
        points = [(self.clock_radius, self.clock_radius), direction_vec, head_1, direction_vec, head_2]

        collide_points = [head_2 - unit_vec * self.hand_radius * (1 - 1 / 15 * np.cos(np.radians(40))),
                          head_2, direction_vec, head_1,
                          head_1 - unit_vec * self.hand_radius * (1 - 1 / 15 * np.cos(np.radians(40)))]

        pg.draw.lines(self.image, Colours.black.value, False, points, width=3)

        line = geometry.LineString(collide_points)
        self.collide_region = geometry.Polygon(line)

        # self.image = arrow_surf
        self.endpoint = pg.Vector2(int(direction_vec.x), int(direction_vec.y))

    def is_clicked(self, pos):
        point = geometry.Point(*pos)
        return self.collide_region.contains(point)

    def click_return(self):
        return self.id


class ClockDraw:
    def __init__(self, size=(1024, 600), parent=None):
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

        self.touch_screen = TouchScreen(self.display_size)

        self.center_offset = self.display_size / 2

        valid_time = False
        start = datetime.datetime.now()
        time = start
        min_ang, hour_ang = 0, 0
        while not valid_time:
            time = start + datetime.timedelta(minutes=randrange(60*24))
            min_ang = time.minute/60 * 360
            hour_ang = (time.hour % 12)/12 * 360 + min_ang / 12

            if abs(min_ang - hour_ang) > 60:
                valid_time = True

        self.time = time
        self.angles = (min_ang, hour_ang)

        self.clock_radius = 250
        self.clock_offset = (self.display_size - pg.Vector2(self.clock_radius * 2, self.clock_radius * 2)) / 2

        self.minute_hand = ClockHand(id="minute", clock_radius=self.clock_radius,
                                     hand_radius=int(self.clock_radius*0.9))
        self.hour_hand = ClockHand(id="hour", clock_radius=self.clock_radius,
                                     hand_radius=int(self.clock_radius * 0.7))

        self.hand_clicked = None

        self.running = False

    def instruction_loop(self):
        self.display_screen.state = 1
        self.display_screen.instruction = None

        button_rect = pg.Rect(self.touch_screen.size - pg.Vector2(150, 150), (100, 100))
        start_button = GameButton(position=button_rect.topleft, size=button_rect.size, text="START", id=1)
        self.touch_screen.sprites = GameObjects([start_button])

        info_rect = pg.Rect(0.3 * self.display_size.x, 0, 0.7 * self.display_size.x, 0.8 * self.display_size.y)
        pg.draw.rect(self.display_screen.surface, Colours.white.value,
                     info_rect)

        self.display_screen.add_multiline_text("Set the Time!", rect=info_rect.scale_by(0.9, 0.9),
                                               font_size=50)

        self.display_screen.add_multiline_text(
            rect=info_rect.scale_by(0.9, 0.9), text=
            "Please set the clock to the time shown in the screen. To do this, drag each clock hand around to the "
            "position that you think it should be in. See the example below.",
            center_vertical=True, font_size=40)


        im_size = pg.Vector2(self.touch_screen.surface.get_size())*0.95
        image_rect = pg.Rect((self.touch_screen.size - im_size)/2, im_size)
        self.touch_screen.load_image("consultation/graphics/instructions/clock_example.png",
                                     pos=image_rect.topleft, size=image_rect.size)

        # self.parent.speak_text("Trace the spiral",
        #                        display_screen=self.display_screen, touch_screen=self.touch_screen)

        self.top_screen.blit(self.display_screen.get_surface(), (0, 0))
        self.bottom_screen.blit(self.touch_screen.get_surface(), (0, 0))
        pg.display.flip()

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

        self.touch_screen.kill_sprites()
        self.touch_screen.refresh()

    def update_display(self):
        self.touch_screen.refresh()
        # self.touch_screen.sprites = GameObjects([self.hour_hand, self.minute_hand])

        self.top_screen.blit(self.display_screen.get_surface(), (0, 0))
        self.bottom_screen.blit(self.touch_screen.get_surface(), (0, 0))
        pg.display.flip()

    def entry_sequence(self):
        # pre-loop initialisation section
        # add everything needed to introduce your module and explain
        # what the users are expected to do (e.g. game rules, aim, etc.)
        self.running = True
        self.instruction_loop()

        pg.draw.circle(self.touch_screen.base_surface, Colours.black.value, self.center_offset, self.clock_radius,
                       width=5)
        self.touch_screen.add_multiline_text(self.time.strftime("%H:%M"), pg.Rect((0, 10), self.display_size),
                                             center_horizontal=True, base=True)

        button_rect = pg.Rect(self.touch_screen.size - pg.Vector2(200, 150), (150, 100))
        submit_button = GameButton(position=button_rect.topleft, size=button_rect.size, text="FINISHED", id=1)

        self.touch_screen.sprites = GameObjects([self.minute_hand, self.hour_hand, submit_button])

        self.update_display()  # render graphics to main consult
        # add code below

    def exit_sequence(self):
        # post-loop completion section
        # maybe add short thank you for completing the section?

        # only OPTIONAL and can leave blank
        rel_pos_min = self.minute_hand.endpoint - pg.Vector2(self.clock_radius, self.clock_radius)

        if np.pi/2 + np.arctan2(*np.flip(rel_pos_min)) > 0:
            min_angle = np.pi/2 + np.arctan2(*np.flip(rel_pos_min))
        else:
            min_angle = 5*np.pi/2 + np.arctan2(*np.flip(rel_pos_min))

        rel_pos_hour = self.hour_hand.endpoint - pg.Vector2(self.clock_radius, self.clock_radius)
        if np.pi / 2 + np.arctan2(*np.flip(rel_pos_hour)) > 0:
            hour_angle = np.pi / 2 + np.arctan2(*np.flip(rel_pos_hour))
        else:
            hour_angle = 5 * np.pi / 2 + np.arctan2(*np.flip(rel_pos_hour))

        print(f"actual min angle:{self.angles[0]}, actual hour angle: {self.angles[1]}")
        print(f"set min angle:{np.degrees(min_angle) % 360}, set hour angle: {np.degrees(hour_angle) % 360}")

        min_error_1 = self.angles[0] - np.degrees(min_angle) % 360
        hour_error_1 = self.angles[1] - np.degrees(hour_angle) % 360

        min_error_2 = self.angles[1] - np.degrees(min_angle) % 360
        hour_error_2 = self.angles[0] - np.degrees(hour_angle) % 360

        threshold = 20

        if (np.linalg.norm([min_error_1, hour_error_1]) <= threshold or
                np.linalg.norm([min_error_2, hour_error_2]) <= threshold):
            print("Pass")
        else:
            print("Fail")

    def get_relative_mose_pos(self):
        if self.parent:
            pos = pg.Vector2(self.parent.get_relative_mose_pos())
        else:
            pos = pg.Vector2(pg.mouse.get_pos())

        return pos

    def loop(self):
        self.entry_sequence()
        while self.running:
            for event in pg.event.get():
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_s:
                        if self.parent:
                            self.parent.take_screenshot("clock")
                    elif event.key == pg.K_ESCAPE:
                        self.running = False

                elif event.type == pg.MOUSEBUTTONDOWN:
                    # do something with mouse click
                    pos = self.get_relative_mose_pos()
                    if self.touch_screen.click_test(pos):
                        # self.exit_sequence()
                        self.running = False
                    else:
                        selection = self.touch_screen.click_test(pos - self.clock_offset)
                        if selection is not None:
                            self.hand_clicked = selection

                elif event.type == pg.MOUSEMOTION and self.hand_clicked is not None:
                    pos = self.get_relative_mose_pos()

                    if self.hand_clicked == "hour":
                        self.hour_hand.update_image(pos - self.center_offset)
                    else:
                        self.minute_hand.update_image(pos - self.center_offset)

                    self.update_display()

                elif event.type == pg.MOUSEBUTTONUP:
                    self.hand_clicked = None

                elif event.type == pg.QUIT:
                    # break the running loop
                    self.running = False

        self.exit_sequence()


def update_time():
    SETUP_CODE = '''
import pygame as pg
from __main__ import ClockHand

clock_hand = ClockHand("hour", clock_radius=250, hand_radius=250*0.7)
'''

    TEST_CODE = '''
clock_hand.update_image(pg.Vector2(0, 100))
    '''
    # timeit.repeat statement
    times = timeit.repeat(setup=SETUP_CODE,
                          stmt=TEST_CODE,
                          number=10000)

    print('Avg update time: {}'.format(min(times)))


if __name__ == "__main__":
    os.chdir("/Users/benhoskings/Documents/Pycharm/Hero_Monitor")
    update_time()
    # Module Testing
    # module_name = ClockDraw()
    # module_name.loop()
    # print("Module run successfully")
