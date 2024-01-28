import math
from enum import Enum

import pygame as pg
import numpy as np
import pandas as pd


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

        if colour:
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

    def add_text(self, text, pos, lines=1, colour=Colours.black, bg_colour=None, location=BlitLocation.topLeft, sprite=False, base=False):
        # pos will be either a tuple (x, y), or BlitPosition

        text_surf = self.font.render(text, True, colour.value)
        if bg_colour:
            bg_surf = pg.Surface(text_surf.get_size(), pg.SRCALPHA)
            bg_surf.fill(bg_colour.value)
            bg_surf.blit(text_surf, (0, 0))
            text_surf = bg_surf

        blitPos = pos
        size = pg.Vector2(text_surf.get_size())
        if location == BlitLocation.centre:
            blitPos -= size / 2
        elif location == BlitLocation.topRight:
            blitPos -= pg.Vector2(size.x, 0)
        elif location == BlitLocation.midTop:
            blitPos -= pg.Vector2(size.x / 2, 0)
        elif location == BlitLocation.midBottom:
            blitPos -= pg.Vector2(size.x / 2, size.y)

        if sprite:
            self.sprite_surface.blit(text_surf, blitPos)
        elif base:
            self.base_surface.blit(text_surf, blitPos)
        else:
            self.surface.blit(text_surf, blitPos)

    def add_multiline_text(self, text, rect, location=BlitLocation.topLeft, center_horizontal=False, center_vertical=False,
                           colour=None, bg_colour=None, font_size=None, base=False):
        rect: pg.Rect

        if colour is None:
            colour = Colours.black

        if font_size == "large":
            self.font = self.fonts.large

        ids = [0]
        line_width = 0
        for idx, word in enumerate(text.split(" ")):
            if word == "\n":
                ids.append(idx)
                line_width = 0
            else:
                width = self.font.size(word + " ")[0]
                if line_width + self.font.size(word)[0] > rect.width:
                    ids.append(idx)
                    line_width = width
                else:
                    line_width += width
        ids.append(len(text.split(" ")))

        height, gap = 0, 10
        text_surfs = []
        for line in range(len(ids)-1):
            line_words = text.replace("\n ", "").split(" ")[ids[line]:ids[line+1]]
            line_text_surf = self.font.render(" ".join(line_words), True, colour.value)

            text_surfs.append(line_text_surf)

            height += line_text_surf.get_height() + gap  # cumulative height with 5px padding

        text_surf = pg.Surface(rect.size, pg.SRCALPHA)
        if bg_colour:
            text_surf.fill(bg_colour.value)
        total_height = sum([surf.get_height() for surf in text_surfs])
        total_height += gap*(len(text_surfs)-1)
        if center_vertical:
            y_offset = (rect.h - total_height) / 2
        else:
            y_offset = 0

        for idx, surf in enumerate(text_surfs):
            if center_horizontal:
                text_surf.blit(surf, ((rect.width - surf.get_width())/2, y_offset + idx * (surf.get_height() + gap)))
            else:
                text_surf.blit(surf, (0, y_offset + idx*(surf.get_height() + gap)))

        blitPos = rect.topleft
        size = rect.size

        # pg.draw.rect(self.surface, Colours.red.value, rect, width=5)

        if location == BlitLocation.centre:
            blitPos -= size / 2
        elif location == BlitLocation.topRight:
            blitPos -= pg.Vector2(size.x, 0)
        elif location == BlitLocation.midTop:
            blitPos -= pg.Vector2(size.x / 2, 0)

        elif base:
            self.base_surface.blit(text_surf, blitPos)
        else:
            self.surface.blit(text_surf, blitPos)

        self.font = self.fonts.normal

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

    def add_speech_bubble(self, rect, pos, border=4, tiers=4, colour=Colours.black, base=False):
        rect: pg.Rect

        inside_tiers = max([2, math.floor(tiers/2)])
        blit_width = border / tiers
        surf = pg.Surface(rect.size, pg.SRCALPHA)
        # surf.fill(Colours.red.value)

        tier_rect = rect
        tier_rect.topleft = (0, 0)
        # create the outside boundary
        for idx, tier in enumerate(range(tiers-1)):
            tier_width = (tiers - idx) * border / tiers

            top_line = pg.Rect((tier_width, tier_rect.top),
                               (tier_rect.width - (1-idx/(tiers-idx))*tier_width * 2, tier_width))
            bottom_line = pg.Rect((tier_width, tier_rect.top + tier_rect.height - tier_width),
                                  (tier_rect.width - (1-idx/(tiers-idx))*tier_width * 2, tier_width))
            left_line = pg.Rect((tier_rect.left, tier_width), (tier_width, tier_rect.height - (1-idx/(tiers-idx))* 2 * tier_width))
            right_line = pg.Rect((tier_rect.left + tier_rect.width - tier_width, tier_width),
                                 (tier_width, tier_rect.height - 2 * (1-idx/(tiers-idx))*tier_width))
            border_lines = [top_line, bottom_line, left_line, right_line]

            for line in border_lines:
                pg.draw.rect(surf, colour.value, line)

            tier_rect = tier_rect.inflate(-(2 * border) / tiers, - (2 * border) / tiers)

        # create inside border
        tier_rect = rect
        tier_rect.topleft = (0, 0)
        tier_rect = tier_rect.inflate(-border*2, -border*2)

        # print(border)
        for idx, count in enumerate(range(inside_tiers)):
            # pg.draw.rect(surf, Colours.red.value, tier_rect, width=1)
            top_line_1 = pg.Rect(tier_rect.topleft,
                                 ((inside_tiers-idx)*blit_width, blit_width))
            top_line_2 = pg.Rect(tier_rect.topright - pg.Vector2((inside_tiers - idx) * blit_width, 0),
                                 ((inside_tiers - idx) * blit_width, blit_width))

            bottom_line_1 = pg.Rect(tier_rect.bottomleft - pg.Vector2(0, blit_width),
                                    ((inside_tiers-idx)*blit_width, blit_width))
            bottom_line_2 = pg.Rect(tier_rect.bottomright - pg.Vector2((inside_tiers - idx) * blit_width, blit_width),
                                 ((inside_tiers - idx) * blit_width, blit_width))

            tier_rect = tier_rect.inflate(0, -blit_width * 2)
            # print(top_line_2)

            # for line in border_lines:
            pg.draw.rect(surf, colour.value, top_line_1)
            pg.draw.rect(surf, colour.value, top_line_2)
            pg.draw.rect(surf, colour.value, bottom_line_1)
            pg.draw.rect(surf, colour.value, bottom_line_2)

        if base:
            self.base_surface.blit(surf, pos)
        else:
            self.surface.blit(surf, pos)

    def refresh(self):
        self.surface = pg.Surface(self.size, pg.SRCALPHA)
        self.sprite_surface = pg.Surface(self.size, pg.SRCALPHA)

    def clear_surfaces(self):
        self.surface = None
        self.base_surface = None
        self.font = None

    def get_surface(self):
        display_surf = self.base_surface.copy()
        display_surf.blit(self.surface, (0, 0))
        display_surf.blit(self.sprite_surface, (0, 0))

        return display_surf

    def scale_surface(self, scale, base=False):
        self.size = pg.Vector2(self.base_surface.get_size()) * scale
        self.surface = pg.transform.scale(self.surface, pg.Vector2(self.surface.get_size()) * scale)
        if base:
            self.base_surface = pg.transform.scale(self.base_surface, pg.Vector2(self.base_surface.get_size()) * scale)
