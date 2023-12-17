import random

import numpy as np
import pygame as pg

speak_1 = np.array([
    # 1  2  3  4  5  6  7  8  9  10 11 12 13 14 15 16
    [0, 0, 0, 0, 0, 3, 3, 3, 3, 3, 3, 0, 0, 0, 0, 0],  # 1
    [0, 0, 0, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 0, 0, 0],  # 2
    [0, 0, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 0, 0],  # 3
    [0, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 0],  # 4
    [0, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 0],  # 5
    [1, 2, 2, 2, 1, 1, 2, 2, 2, 2, 1, 1, 2, 2, 2, 1],  # 6
    [1, 2, 2, 2, 1, 1, 2, 2, 2, 2, 1, 1, 2, 2, 2, 1],  # 7
    [1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1],  # 8
    [1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1],  # 9
    [1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1],  # 10
    [1, 2, 2, 2, 2, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 1],  # 11
    [0, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 0],  # 12
    [0, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 0],  # 13
    [0, 0, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 0, 0],  # 14
    [0, 0, 0, 1, 1, 2, 2, 2, 2, 2, 2, 1, 1, 0, 0, 0],  # 15
    [0, 0, 0, 0, 0, 1, 2, 2, 2, 2, 1, 0, 0, 0, 0, 0],  # 16
    [0, 0, 0, 1, 1, 2, 2, 2, 2, 2, 2, 1, 1, 0, 0, 0],
    [0, 0, 1, 3, 3, 2, 2, 2, 2, 2, 2, 3, 3, 1, 0, 0],
])

speak_2 = np.array([
    # 1  2  3  4  5  6  7  8  9  10 11 12 13 14 15 16
    [0, 0, 0, 0, 0, 3, 3, 3, 3, 3, 3, 0, 0, 0, 0, 0],  # 1
    [0, 0, 0, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 0, 0, 0],  # 2
    [0, 0, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 0, 0],  # 3
    [0, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 0],  # 4
    [0, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 0],  # 5
    [1, 2, 2, 2, 1, 1, 2, 2, 2, 2, 1, 1, 2, 2, 2, 1],  # 6
    [1, 2, 2, 2, 1, 1, 2, 2, 2, 2, 1, 1, 2, 2, 2, 1],  # 7
    [1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1],  # 8
    [1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1],  # 9
    [1, 2, 2, 2, 2, 2, 1, 1, 1, 1, 2, 2, 2, 2, 2, 1],  # 10
    [1, 2, 2, 2, 2, 1, 5, 5, 5, 5, 1, 2, 2, 2, 2, 1],  # 11
    [0, 1, 2, 2, 2, 2, 1, 1, 1, 1, 2, 2, 2, 2, 1, 0],  # 12
    [0, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 0],  # 13
    [0, 0, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 0, 0],  # 14
    [0, 0, 0, 1, 1, 2, 2, 2, 2, 2, 2, 1, 1, 0, 0, 0],  # 15
    [0, 0, 0, 0, 0, 1, 2, 2, 2, 2, 1, 0, 0, 0, 0, 0],  # 16
    [0, 0, 0, 1, 1, 2, 2, 2, 2, 2, 2, 1, 1, 0, 0, 0],  # 17
    [0, 0, 1, 3, 3, 2, 2, 2, 2, 2, 2, 3, 3, 1, 0, 0],  # 18
])

smile = np.array([
    # 1  2  3  4  5  6  7  8  9  10 11 12 13 14 15 16
    [0, 0, 0, 0, 0, 3, 3, 3, 3, 3, 3, 0, 0, 0, 0, 0],  # 1
    [0, 0, 0, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 0, 0, 0],  # 2
    [0, 0, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 0, 0],  # 3
    [0, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 0],  # 4
    [0, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 0],  # 5
    [1, 2, 2, 2, 4, 4, 2, 2, 2, 2, 4, 4, 2, 2, 2, 1],  # 6
    [1, 2, 2, 2, 4, 4, 2, 2, 2, 2, 4, 4, 2, 2, 2, 1],  # 7
    [1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1],  # 8
    [1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1],  # 9
    [1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1],  # 10
    [1, 2, 2, 2, 2, 4, 2, 2, 2, 2, 4, 2, 2, 2, 2, 1],  # 11
    [0, 1, 2, 2, 2, 2, 4, 4, 4, 4, 2, 2, 2, 2, 1, 0],  # 12
    [0, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 0],  # 13
    [0, 0, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 0, 0],  # 14
    [0, 0, 0, 1, 1, 2, 2, 2, 2, 2, 2, 1, 1, 0, 0, 0],  # 15
    [0, 0, 0, 0, 0, 1, 2, 2, 2, 2, 1, 0, 0, 0, 0, 0],  # 16
    [0, 0, 0, 1, 1, 2, 2, 2, 2, 2, 2, 1, 1, 0, 0, 0],
    [0, 0, 1, 3, 3, 2, 2, 2, 2, 2, 2, 3, 3, 1, 0, 0],
])

whistle = np.array([
    # 1  2  3  4  5  6  7  8  9  10 11 12 13 14 15 16
    [0, 0, 0, 0, 0, 3, 3, 3, 3, 3, 3, 0, 0, 0, 0, 0],  # 1
    [0, 0, 0, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 0, 0, 0],  # 2
    [0, 0, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 0, 0],  # 3
    [0, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 0],  # 4
    [0, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 6, 1, 0],  # 5
    [1, 2, 2, 2, 4, 4, 2, 2, 2, 2, 4, 4, 2, 6, 6, 1],  # 6
    [1, 2, 2, 2, 4, 4, 2, 2, 2, 2, 4, 4, 2, 6, 2, 6],  # 7
    [1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 6, 6, 2, 1],  # 8
    [1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 6, 6, 2, 1],  # 9
    [1, 2, 2, 2, 2, 2, 2, 2, 2, 1, 2, 2, 2, 2, 2, 1],  # 10
    [1, 2, 2, 2, 2, 2, 2, 2, 1, 5, 1, 2, 2, 2, 2, 1],  # 11
    [0, 1, 2, 2, 2, 2, 2, 2, 2, 1, 2, 2, 2, 2, 1, 0],  # 12
    [0, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 0],  # 13
    [0, 0, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 0, 0],  # 14
    [0, 0, 0, 1, 1, 2, 2, 2, 2, 2, 2, 1, 1, 0, 0, 0],  # 15
    [0, 0, 0, 0, 0, 1, 2, 2, 2, 2, 1, 0, 0, 0, 0, 0],  # 16
    [0, 0, 0, 1, 1, 2, 2, 2, 2, 2, 2, 1, 1, 0, 0, 0],
    [0, 0, 1, 3, 3, 2, 2, 2, 2, 2, 2, 3, 3, 1, 0, 0],
])

skin_tones = ["#8D5524", "#C68642", "#E0AC69", "#F1C27D", "#FFDBAC"]


class Avatar:
    def __init__(self, state=0, face_colour=None, size=(128, 128 * 1.125)):
        self.skin_tones = skin_tones

        if face_colour:
            self.preset = False
            self.face_idx = None
            self.face_colour = face_colour
        else:
            self.face_idx = np.random.randint(len(skin_tones))
            self.preset = True
            self.face_colour = pg.Color(self.skin_tones[self.face_idx])

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
