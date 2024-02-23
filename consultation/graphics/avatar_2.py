import os
import random
import re
import time

import pygame as pg

from consultation.screen import Screen, Colours


class AvatarV2:
    def __init__(self, scale=pg.Vector2(1, 1)):
        gender = ("male", "female")[random.randint(0, 1)]
        print(gender)
        self.image = pg.image.load(f"consultation/graphics/sprites/avatar_{gender}.png")
        self.image = pg.transform.scale_by(self.image, scale)
        if gender == "female":
            self.mouth_pos = pg.Vector2(46*scale.x, 54*scale.y)
        else:
            self.mouth_pos = pg.Vector2(53*scale.x, 59*scale.y)

        self.mouth_sprites = [pg.image.load(f"consultation/graphics/sprites/mouths/mouth_{idx}.png")
                              for idx in range(12)]

        if scale.x != 1 or scale.y != 1:
            self.mouth_sprites = [pg.transform.scale_by(surface, scale*0.7) for surface in self.mouth_sprites]

        self.mouth_sizes = [pg.Vector2(surface.get_size()) for surface in self.mouth_sprites]
        self.mouth_idx = 0

    def get_surface(self):
        surface = self.image.copy()
        surface.blit(self.mouth_sprites[self.mouth_idx], self.mouth_pos - self.mouth_sizes[self.mouth_idx]/2)
        return surface


if __name__ == "__main__":
    os.chdir("/Users/benhoskings/Documents/Pycharm/Hero_Monitor")
    # os.chdir('/Users/benhoskings/Documents/Projects/hero-monitor')
    sprite_path = "consultation/graphics/sprites"

    pg.init()
    window = pg.display.set_mode(pg.Vector2(512, 512))

    avatar = AvatarV2(scale=pg.Vector2(3, 3))

    screen = Screen(window.get_size(), colour=Colours.white)
    start = time.monotonic()

    text = "welcome       to      "

    text = text.replace(" ", "0 ")
    rep_1 = {"th": "11 ", "sh": "9 ", "ch": "9 ", "ee": "3 "}
    rep_2 = {"a": "1 ", "e": "1 ", "i": "1 ", "o": "2 ", "c": "4 ", "d": "4 ", "g": "4 ",
             "k": "4 ", "n": "4 ", "s": "4 ", "t": "3 ", "x": "4 ", "y": "4 ", "z": "4 ",
             "q": "5 ", "w": "5 ", "b": "6 ", "m": "6 ", "p": "6 ", "l": "7 ", "f": "8 ",
             "v": "8 ", "j": "9 ", "r": "10", "h": "1 ", "u": "2 "}  # define desired replacements here}

    # use these three lines to do the replacement
    rep_1 = dict((re.escape(k), v) for k, v in rep_1.items())
    # Python 3 renamed dict.iteritems to dict.items so use rep_1.items() for latest versions
    pattern = re.compile("|".join(rep_1.keys()))
    text = pattern.sub(lambda m: rep_1[re.escape(m.group(0))], text)

    rep_2 = dict((re.escape(k), v) for k, v in rep_2.items())
    # Python 3 renamed dict.iteritems to dict.items so use rep_1.items() for latest versions
    pattern = re.compile("|".join(rep_2.keys()))
    text = pattern.sub(lambda m: rep_2[re.escape(m.group(0))], text).strip()

    mouth_ids = [int(num) for num in text.split(" ")]
    seq_idx = 0
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                quit()

        if time.monotonic() - start > 0.25:
            screen.refresh()
            avatar.mouth_idx = mouth_ids[seq_idx]
            screen.add_surf(avatar.get_surface(), (0, 0))
            window.blit(screen.get_surface(), (0, 0))
            pg.display.update()
            start = time.monotonic()
            seq_idx = (seq_idx + 1) % len(mouth_ids)