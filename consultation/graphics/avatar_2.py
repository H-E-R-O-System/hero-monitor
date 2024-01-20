import time, random

import pygame as pg
from math import floor
from sprite_set import SpriteSet
from consultation.screen import Screen, Colours
import os


class AvatarV2:
    def __init__(self):
        self.mouth_sprites = SpriteSet("consultation/graphics/mouth_sprites.png", 4, pg.Vector2(64, 64), pg.Vector2(5, 5))
        self.mouth_sprites.scale_sprites(4)
        self.mouth_idx = 0
        gender = ("male", "female")[random.randint(0, 1)]
        print(gender)
        self.image = pg.image.load(f"consultation/graphics/sprites/avatar_{gender}.png")

    def update(self):
        self.mouth_sprites.update_active(self.mouth_idx)


if __name__ == "__main__":
    os.chdir("/Users/benhoskings/Documents/Pycharm/Hero_Monitor")
    # os.chdir('/Users/benhoskings/Documents/Projects/hero-monitor')
    sprite_path = "consultation/graphics/sprites"

    pg.init()
    window = pg.display.set_mode(pg.Vector2(256, 256))

    avatar = AvatarV2()

    screen = Screen((256, 256), colour=Colours.white.value)
    screen.load_image(os.path.join(sprite_path, "face1.png"), base=True, scale=pg.Vector2(4, 4))
    screen.refresh()
    window.blit(screen.surface, (0, 0))
    pg.display.update()

    start = time.monotonic()

    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                quit()

        if time.monotonic() - start > 1:
            screen.refresh()
            avatar.mouth_idx = (avatar.mouth_idx + 1) % avatar.mouth_sprites.length
            avatar.update()
            screen.add_surf(avatar.mouth_sprites.active, (0, 0))
            window.blit(screen.surface, (0, 0))
            pg.display.update()
            start = time.monotonic()