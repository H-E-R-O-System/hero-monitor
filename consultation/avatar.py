import random

import numpy as np
import pygame as pg

class Avatar:
    def __init__(self, state=0, face_colour=None, size=(128, 128 * 1.125)):
        self.size = size
        self.colours = None
        self.speak_surfs = None
        self.smile = None
        self.whistle_surfs = None

        self.update_colours()

        # State 0: Smile, 1: Speak, 2: Whistle
        self.state = state
        self.speak_state = 0
        self.whistle_state = 0

        gender = ("male", "female")[random.randint(0, 1)]
        self.image = pg.image.load(f"consultation/graphics/sprites/avatar_{gender}.png")
        self.image = pg.transform.scale(self.image, size)
        self.size = self.image.get_size()

        self.mode = 0

    def update_colours(self):
        self.colours = [pg.Color(0, 0, 0, 0), pg.Color(55, 55, 55, 255), self.face_colour,
                        pg.Color("#ADCAE6"), pg.Color(0, 0, 0), pg.Color("#D37070")]

        self.speak_surfs = [self.convert_array_to_surf(arr, self.size) for arr in [speak_1, speak_2]]
        self.smile = self.convert_array_to_surf(smile, self.size)
        self.whistle_surfs = [self.convert_array_to_surf(whistle, self.size, edit_colour=note_colour) for note_colour in
                              [pg.Color("#1a6bff"), pg.Color("#ffae1a")]]

    def convert_array_to_surf(self, array, size=None, edit_colour=pg.Color("#ffae1a")):

        array = array.transpose()
        surf = pg.Surface(array.shape[:2], pg.SRCALPHA)
        for key, colour in zip(range(7), self.colours + [edit_colour]):
            coords = np.transpose(np.nonzero(array == key))
            for coord in coords:
                surf.set_at(coord, colour)

        if size:
            surf = pg.transform.scale(surf, size)

        return surf

    def get_surface(self):
        if self.mode == 0:
            return self.image
        else:
            if self.state == 0:
                return self.smile
            elif self.state == 1:
                return self.speak_surfs[self.speak_state]
            else:
                return self.whistle_surfs[self.whistle_state]
