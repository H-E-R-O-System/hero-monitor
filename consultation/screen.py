import math
from enum import Enum

import pygame as pg


class Colours(Enum):
    clear = pg.SRCALPHA
    white = pg.Color(255, 255, 255)
    black = pg.Color(1, 1, 1)
    darkGrey = pg.Color(60, 60, 60)
    midGrey = pg.Color(150, 150, 150)
    lightGrey = pg.Color(200, 200, 200)
    green = pg.Color(69, 181, 67)
    red = pg.Color(181, 67, 67)
    shadow = pg.Color(180, 180, 180)
    blue = pg.Color(67, 113, 181)
    yellow = pg.Color(252, 198, 3)


class BlitLocation(Enum):
    topLeft = 0
    midTop = 1
    topRight = 2
    bottomLeft = 3
    midBottom = 4
    bottomRight = 5
    midLeft = 6
    midRight = 7
    centre = 8


class BlitPosition(Enum):
    topLeft = 0
    midTop = 1
    topRight = 2
    bottomLeft = 3
    midBottom = 4
    bottomRight = 5
    midLeft = 6
    midRight = 7
    centre = 8


class Fonts:
    def __init__(self):
        self.large = pg.font.Font("consultation/fonts/calibri-regular.ttf", size=50)
        self.normal = pg.font.Font("consultation/fonts/calibri-regular.ttf", size=30)
        self.small = pg.font.Font("consultation/fonts/calibri-regular.ttf", size=15)
        self.custom = self.normal

    def update_custom(self, size):
        self.custom = pg.font.Font("fonts/calibri-regular.ttf", size=size)


class Screen:
    def __init__(self, size, font=None, colour=None):
        self.size = pg.Vector2(size)
        self.base_surface = pg.Surface(size, pg.SRCALPHA)
        self.surface = pg.Surface(size, pg.SRCALPHA)
        self.sprite_surface = pg.Surface(size, pg.SRCALPHA)
        if font:
            self.fonts = Fonts()
            self.font: pg.font.Font = font
        else:
            self.fonts = Fonts()
            self.font = self.fonts.normal

        if not type(colour) == pg.Color:
            colour = colour.value

        self.colour = colour
        if colour:
            self.base_surface.fill(colour)

    def add_surf(self, surf: pg.Surface, pos=(0, 0), base=False, location=BlitLocation.topLeft, sprite=False):
        surf_rect = pg.Rect(pos, surf.get_size())

        if location == BlitLocation.centre:
            surf_rect.topleft -= pg.Vector2(surf_rect.size) / 2
        elif location == BlitLocation.topRight:
            surf_rect.x -= surf_rect.width
        elif location == BlitLocation.bottomLeft:
            surf_rect.y -= surf_rect.height
        elif location == BlitLocation.midBottom:
            surf_rect.y -= surf_rect.height
            surf_rect.x -= surf_rect.width / 2

        if sprite:
            self.sprite_surface.blit(surf, surf_rect.topleft)
        elif base:
            self.base_surface.blit(surf, surf_rect.topleft)
        else:
            self.surface.blit(surf, surf_rect.topleft)

    def load_image(self, path, pos=(0, 0), fill=False, base=False, size=None, scale=None, location=BlitLocation.topLeft):
        image = pg.image.load(path)

        if size:
            image = pg.transform.scale(image, size)
        elif scale:
            image = pg.transform.scale(image, (image.get_size()[0] * scale.x, image.get_size()[1] * scale.y))
        elif fill:
            image = pg.transform.scale(image, self.size)

        imageRect = pg.Rect(pos, image.get_size())

        if location == BlitLocation.centre:
            imageRect.topleft = pg.Vector2(imageRect.topleft) - pg.Vector2(imageRect.size) / 2
        elif location == BlitLocation.topRight:
            imageRect.x -= imageRect.width

        if base:
            self.base_surface.blit(image, imageRect.topleft)
        else:
            self.surface.blit(image, imageRect.topleft)

    def add_image(self, image, pos=pg.Vector2(0, 0), fill=False, scale=None, location=BlitLocation.topLeft, base=False):

        if base:
            surf = self.base_surface
        else:
            surf = self.surface

        if scale:
            image = pg.transform.scale(image, (image.get_size()[0] * scale.x, image.get_size()[1] * scale.y))
        elif fill:
            image = pg.transform.scale(image, self.size)

        size = pg.Vector2(image.get_size())
        if location == BlitLocation.centre:

            surf.blit(image, pos - size / 2)
        elif location == BlitLocation.midBottom:
            newPos = pg.Vector2(pos.x - (size.x / 2), pos.y - size.y)
            surf.blit(image, newPos)
        else:
            surf.blit(image, pos)

    def add_text(self, text, pos, lines=1, colour=Colours.black, location=BlitLocation.topLeft, sprite=False, base=False):
        # pos will be either a tuple (x, y), or BlitPosition

        textSurf = self.font.render(text, True, colour.value)

        blitPos = pos
        size = pg.Vector2(textSurf.get_size())
        if location == BlitLocation.centre:
            blitPos -= size / 2
        elif location == BlitLocation.topRight:
            blitPos -= pg.Vector2(size.x, 0)
        elif location == BlitLocation.midTop:
            blitPos -= pg.Vector2(size.x / 2, 0)
        elif location == BlitLocation.midBottom:
            blitPos -= pg.Vector2(size.x / 2, size.y)

        if sprite:
            self.sprite_surface.blit(textSurf, blitPos)
        elif base:
            self.base_surface.blit(textSurf, blitPos)
        else:
            self.surface.blit(textSurf, blitPos)

    def add_multiline_text(self, text, pos, lines=None, location=BlitLocation.topLeft, sprite=False, base=False):
        if not lines:
            lines = math.ceil(self.font.render(text, True, Colours.black.value).get_width() / self.size.x)

        text_length = len(text)
        text_per_line = math.floor(text_length / lines)
        height, gap = 0, 10
        text_surfs = []
        for line in range(lines):
            line_text = text[text_per_line*line:min(text_per_line*(line + 1), text_length)]
            line_text_surf = self.font.render(line_text, True, Colours.black.value)

            text_surfs.append(line_text_surf)

            height += line_text_surf.get_height() + gap # cumulative height with 5px padding

        max_width = max([surf.get_width() for surf in text_surfs])
        text_surf = pg.Surface((max_width, height - gap), pg.SRCALPHA)
        for idx, surf in enumerate(text_surfs):
            text_surf.blit(surf, (0, idx*(surf.get_height() + gap)))

        blitPos = pos
        size = pg.Vector2(text_surf.get_size())
        if location == BlitLocation.centre:
            blitPos -= size / 2
        elif location == BlitLocation.topRight:
            blitPos -= pg.Vector2(size.x, 0)
        elif location == BlitLocation.midTop:
            blitPos -= pg.Vector2(size.x / 2, 0)

        if sprite:
            self.sprite_surface.blit(text_surf, pos)
        elif base:
            self.base_surface.blit(text_surf, blitPos)
        else:
            self.surface.blit(text_surf, blitPos)

    def create_layered_shape(self, pos, shape, size, number, colours, offsets,
                             radii, offsetWidth=False, offsetHeight=False, base=False):
        # create surfaces
        surf = pg.Surface(size, pg.SRCALPHA)
        center = size / 2

        for layer in range(number):
            currentOffset = (0, 0)
            if type(offsets[0]) == pg.Vector2:
                currentOffset = pg.Vector2(0, 0)
            elif type(offsets[0]) == pg.Rect:
                currentOffset = pg.Rect(0, 0, 0, 0)

            for offset in offsets[0:layer + 1]:
                if type(offset) == pg.Vector2:
                    currentOffset += offset
                elif type(offset) == pg.Rect:
                    currentOffset = pg.Rect(pg.Vector2(currentOffset.topleft) + pg.Vector2(offset.topleft),
                                            pg.Vector2(currentOffset.size) + pg.Vector2(offset.size))

            rect = pg.Rect(0, 0, 0, 0)
            if type(currentOffset) == pg.Vector2:
                rect = pg.Rect((0, 0), size - 2 * currentOffset)
                rect.center = center
            elif type(currentOffset) == pg.Rect:
                rect = pg.Rect((currentOffset.x, currentOffset.w), (size.x - currentOffset.x - currentOffset.y,
                                                                    size.y - currentOffset.w - currentOffset.h))

            if shape == "rectangle":
                pg.draw.rect(surf, colours[layer], rect, border_radius=radii[layer])
            else:
                pg.draw.ellipse(surf, colours[layer].value, rect)

        offset = pg.Vector2(size)
        offset.x *= offsetWidth
        offset.y *= offsetHeight

        if base:
            self.base_surface.blit(surf, pos - offset)
        else:
            self.surface.blit(surf, pos - offset)

    def update_pixels(self, pos, colour=Colours.black.value, base=False, width=3):
        pad = (width - 1) / 2
        for x_pos in range(int(pos[0] - pad), int(pos[0] + 1 + pad)):
            for y_pos in range(int(pos[1] - pad), int(pos[1] + 1 + pad)):
                # if np.all(pos != np.array([x_pos, y_pos])):
                #     colour = pg.Color(colour.r, colour.g, colour.b, 0)
                # else:
                #     colour = pg.Color(colour.r, colour.g, colour.b, 255)

                if base:
                    self.base_surface.set_at((x_pos, y_pos), colour)
                else:
                    self.surface.set_at((x_pos, y_pos), colour)

        # new_array[np.int16(positions[0, :]), np.int16(positions[1, :]), :] = [0, 0, 0]
        # new_surf = pg.surfarray.make_surface(new_array)
        # new_surf.set_alpha()
        # self.surface = new_surf

    def refresh(self):
        self.size = pg.Vector2(self.base_surface.get_size())
        self.surface = self.base_surface.copy()
        self.sprite_surface = pg.Surface(self.size, pg.SRCALPHA)

    def clear_surfaces(self):
        self.surface = None
        self.base_surface = None
        self.font = None

    def get_surface(self, sprites=False):

        if sprites:
            self.surface.blit(self.sprite_surface, (0, 0))

        return self.surface

    def scale_surface(self, scale, base=False):
        self.size = pg.Vector2(self.base_surface.get_size()) * scale
        self.surface = pg.transform.scale(self.surface, pg.Vector2(self.surface.get_size()) * scale)
        if base:
            self.base_surface = pg.transform.scale(self.base_surface, pg.Vector2(self.base_surface.get_size()) * scale)
