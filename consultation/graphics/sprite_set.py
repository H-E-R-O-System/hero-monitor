import cv2
import pygame as pg

clear = pg.SRCALPHA


class SpriteSet:
    def __init__(self, path, number, size, space):
        self.spriteSheet = cv2.imread(path, cv2.IMREAD_UNCHANGED)
        self.sprites = []

        for num in range(number):
            rect = pg.Rect(pg.Vector2(space.x + (size.x + space.x) * num, space.y), size)
            imageData = self.spriteSheet[rect.top:rect.bottom, rect.left:rect.right, :]
            formattedImage = cv2.cvtColor(imageData, cv2.COLOR_BGRA2RGBA)
            surf = pg.Surface((formattedImage.shape[1], formattedImage.shape[0]), pg.SRCALPHA)

            for row in range(formattedImage.shape[0]):
                for col in range(formattedImage.shape[1]):
                    c_vals = [int(val) for val in formattedImage[row, col]]
                    colour = pg.Color(*c_vals)
                    surf.set_at((col, row), colour)

            self.sprites.append(surf)

        self.length = number
        self.active = self.sprites[0]

    def scale_sprites(self, scale):
        for (idx, surf) in enumerate(self.sprites):
            scaledImage = pg.transform.scale(surf, pg.Vector2(surf.get_size()) * scale)
            self.sprites[idx] = scaledImage

    def update_active(self, idx):
        self.active = self.sprites[idx]
