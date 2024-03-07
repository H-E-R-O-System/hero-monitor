import os
import random
import re
import time

import pygame as pg

from consultation.screen import Screen, Colours


class Avatar:
    def __init__(self, size=pg.Vector2(420, 420)):
        avatar_base_path = "consultation/graphics/avatars"
        avatar_paths = [os.path.join(avatar_base_path, avatar_file) for avatar_file in
                        os.listdir(avatar_base_path) if (".png" in avatar_file)]

        # gender =
        # self.image = pg.image.load(f"consultation/graphics/sprites/avatar_{gender}.png")
        self.image = pg.image.load(random.choice(avatar_paths))

        if size:
            self.size = pg.Vector2(size)
            prev_size = pg.Vector2(self.image.get_size())
            self.image = pg.transform.scale(self.image, size)
            scale = pg.Vector2(self.size.x / prev_size.x, self.size.y / prev_size.y)
        else:
            self.size = pg.Vector2(self.image.get_size())
            scale = pg.Vector2(1, 1)

        self.mouth_sprites = [pg.image.load(f"consultation/graphics/sprites/mouths/mouth_{idx}.png")
                              for idx in range(1, 13)]

        if scale.x != 1 or scale.y != 1:
            self.mouth_sprites = [pg.transform.scale_by(surface, scale) for surface in self.mouth_sprites]

        self.mouth_idx = 0

    def get_surface(self):
        surface = self.image.copy()
        if self.mouth_idx > 0:
            surface.blit(self.mouth_sprites[self.mouth_idx], (0, 0))
        return surface


if __name__ == "__main__":
    os.chdir("/Users/benhoskings/Documents/Pycharm/Hero_Monitor")
    # os.chdir('/Users/benhoskings/Documents/Projects/hero-monitor')
    sprite_path = "consultation/graphics/sprites"

    pg.init()
    window = pg.display.set_mode(pg.Vector2(512, 512))

    avatar = Avatar(size=(512, 512))

    screen = Screen(window.get_size(), colour=Colours.white)
    start = time.monotonic()

    text = "welcome       to      "

    text = text.replace(" ", "0 ")
    rep_1 = {"th": "8 ", "sh": "9 ", "ch": "9 ", "ee": "7 "}
    rep_2 = {"a": "0 ", "e": "0 ", "i": "0 ",
             "o": "1 ",
             "c": "2 ", "d": "2 ", "n": "2 ", "s": "2 ", "t": "2 ", "x": "2 ", "y": "2 ", "z": "z ",
             "g": "3 ", "k": "3 ",
             "l": "4 ",
             "b": "5 ", "m": "5 ", "p": "5 ",
             "f": "6 ", "v": "6 ",
             "j": "9 ",
             "u": "10 ",
             "q": "11 ", "w": "11 ", "h": "", }  # define desired replacements here

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