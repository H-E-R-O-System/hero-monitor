from enum import Enum

import numpy as np
import pygame as pg


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


class Screen:
    def __init__(self, size, colour=None):
        self.size = pg.Vector2(size)
        self.baseSurface = pg.Surface(size, pg.SRCALPHA)
        self.surface = pg.Surface(size, pg.SRCALPHA)
        self.colour = colour
        if colour:
            self.baseSurface.fill(colour)

    def plot_spiral(A, B, t_max=4, num_points=1000):

        t = np.linspace(0, t_max * np.pi, num_points)
        x = A * t * np.cos(B * t)
        y = A * t * np.sin(B * t)

        plt.figure(figsize=(13, 13))
        # Plot the spiral
        plt.plot(x, y, linewidth=5)
        # Turn off x-axis ticks and labels
        plt.xticks([])
        plt.xlabel('')

        # Turn off y-axis ticks and labels
        plt.yticks([])
        plt.ylabel('')

        plt.gca().set_aspect('equal', adjustable='box')
        plt.savefig('spiral_plot.png')

    def loadImage(self, path, pos=(0, 0), fill=False, base=False, size=None, scale=None, location=BlitLocation.topLeft):
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
            self.baseSurface.blit(image, imageRect.topleft)
        else:
            self.surface.blit(image, imageRect.topleft)

    def addImage(self, image, pos=pg.Vector2(0, 0), fill=False, scale=None, location=BlitLocation.topLeft, base=False):

        if base:
            surf = self.baseSurface
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

    def createLayeredShape(self, pos, shape, size, number, colours, offsets,
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
            self.baseSurface.blit(surf, pos - offset)
        else:
            self.surface.blit(surf, pos - offset)

    # def updatePixels(self, pos):
    #     for x_pos in range(int(pos[0]-1), int(pos[0]+2)):
    #         for y_pos in range(int(pos[1] - 1), int(pos[1] + 2)):
    #             self.surface.set_at((x_pos, y_pos), pg.Color(255, 0, 0))

    # def updatePixels(self, angles, scaling_factor, turns_factor):
    #     if angles[-1] != angles[-2]:
    #         num_points = 10  # Adjust the number of points as needed
    #         theta = np.linspace(angles[-2], angles[-1], num_points)
    #         r = scaling_factor * np.exp(turns_factor * theta)
    #         x = np.round(r * np.cos(theta)).astype(int)
    #         y = np.round(r * np.sin(theta)).astype(int)
    #         for x_pos in x:
    #             for y_pos in y:
    #                 self.surface.set_at((x_pos, y_pos), pg.Color(255, 0, 0))

    def updatePixels(self, angles, scaling_factor, turns_factor):
        num_points = 100  # Adjust the number of points as needed
        theta = np.linspace(0, angles[-1], num_points)
        r = scaling_factor * np.exp(turns_factor * theta)
        x = np.round(r * np.cos(theta)).astype(int)
        y = np.round(r * np.sin(theta)).astype(int)
        for i in range(len(x)):
            x_pos = x[i]
            y_pos = y[i]
            if 0 <= x_pos < self.surface.get_width() and 0 <= y_pos < self.surface.get_height():
                print(x_pos,y_pos)
                self.surface.set_at((x_pos, y_pos), pg.Color(255, 0, 0))


    def refresh(self):
        self.size = pg.Vector2(self.baseSurface.get_size())
        self.surface = self.baseSurface.copy()

    def clearSurfaces(self):
        self.surface = None
        self.baseSurface = None
        self.font = None

    def getSurface(self, image, pos=(0, 0), location=BlitLocation.topLeft):
        imageRect = pg.Rect(pos, image.get_size())

        if location == BlitLocation.centre:
            imageRect.topleft = pg.Vector2(imageRect.topleft) - pg.Vector2(imageRect.size) / 2
        elif location == BlitLocation.topRight:
            imageRect.x -= imageRect.width

        surf = pg.Surface(self.size, pg.SRCALPHA)
        surf.blit(image, imageRect.topleft)

        surfaceCopy = self.surface.copy()
        surfaceCopy.blit(surf, (0, 0))

        return surfaceCopy

    def scaleSurface(self, scale, base=False):
        self.size = pg.Vector2(self.baseSurface.get_size()) * scale
        self.surface = pg.transform.scale(self.surface, pg.Vector2(self.surface.get_size()) * scale)
        if base:
            self.baseSurface = pg.transform.scale(self.baseSurface, pg.Vector2(self.baseSurface.get_size()) * scale)
