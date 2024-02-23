import matplotlib.pyplot as plt
from screen import Screen
import matplotlib.pyplot as plt

from screen import Screen


def plot_spiral(A, B, t_max=4, num_points=1000):

    t = np.linspace(0, t_max * np.pi, num_points)
    x = A * t * np.cos(B * t)
    y = A * t * np.sin(B * t)

    plt.figure(figsize=(13,13))
    #Plot the spiral
    plt.plot(x, y ,linewidth=5)
    #Turn off x-axis ticks and labels
    plt.xticks([])
    plt.xlabel('')

    # Turn off y-axis ticks and labels
    plt.yticks([])
    plt.ylabel('')

    plt.gca().set_aspect('equal', adjustable='box')
    plt.savefig('spiral_plot.png')


from consultation.screen import Colours, BlitLocation, Fonts
import numpy as np
import pygame as pg
import time
import pandas as pd
import os


# def load_image(self, path, pos=(0, 0), fill=False, base=False, size=None, scale=None, location=BlitLocation.topLeft):
#     image = pg.image.load(path)
#
#     if size:
#         image = pg.transform.scale(image, size)
#     elif scale:
#         image = pg.transform.scale(image, (image.get_size()[0] * scale.x, image.get_size()[1] * scale.y))
#     elif fill:
#         image = pg.transform.scale(image, self.size)
#
#     imageRect = pg.Rect(pos, image.get_size())
#
#     if location == BlitLocation.centre:
#         imageRect.topleft = pg.Vector2(imageRect.topleft) - pg.Vector2(imageRect.size) / 2
#     elif location == BlitLocation.topRight:
#         imageRect.x -= imageRect.width
#
#     if base:
#         self.base_surface.blit(image, imageRect.topleft)
#     else:
#         self.surface.blit(image, imageRect.topleft)

# def add_image(self, image, pos=pg.Vector2(0, 0), fill=False, scale=None, location=BlitLocation.topLeft, base=False):
#
#     if base:
#         surf = self.base_surface
#     else:
#         surf = self.surface
#
#     if scale:
#         image = pg.transform.scale(image, (image.get_size()[0] * scale.x, image.get_size()[1] * scale.y))
#     elif fill:
#         image = pg.transform.scale(image, self.size)
#
#     size = pg.Vector2(image.get_size())
#     if location == BlitLocation.centre:
#
#         surf.blit(image, pos - size / 2)
#     elif location == BlitLocation.midBottom:
#         newPos = pg.Vector2(pos.x - (size.x / 2), pos.y - size.y)
#         surf.blit(image, newPos)
#     else:
#         surf.blit(image, pos)

# def add_text(self, text, pos, lines=1, location=BlitLocation.topLeft, base=False):
#     # pos will be either a tuple (x, y), or BlitPosition
#
#     textSurf = self.font.render(text, True, pg.Color(0, 0, 0), )
#
#     blitPos = pos
#     size = pg.Vector2(textSurf.get_size())
#     if location == BlitLocation.centre:
#         blitPos -= size / 2
#     elif location == BlitLocation.topRight:
#         blitPos -= pg.Vector2(size.x, 0)
#     elif location == BlitLocation.midTop:
#         blitPos -= pg.Vector2(size.x / 2, 0)
#
#     if base:
#         self.base_surface.blit(textSurf, blitPos)
#     else:
#         self.surface.blit(textSurf, blitPos)

# def create_layered_shape(self, pos, shape, size, number, colours, offsets,
#                          radii, offsetWidth=False, offsetHeight=False, base=False):
#     # create surfaces
#     surf = pg.Surface(size, pg.SRCALPHA)
#     center = size / 2
#
#     for layer in range(number):
#         currentOffset = (0, 0)
#         if type(offsets[0]) == pg.Vector2:
#             currentOffset = pg.Vector2(0, 0)
#         elif type(offsets[0]) == pg.Rect:
#             currentOffset = pg.Rect(0, 0, 0, 0)
#
#         for offset in offsets[0:layer + 1]:
#             if type(offset) == pg.Vector2:
#                 currentOffset += offset
#             elif type(offset) == pg.Rect:
#                 currentOffset = pg.Rect(pg.Vector2(currentOffset.topleft) + pg.Vector2(offset.topleft),
#                                         pg.Vector2(currentOffset.size) + pg.Vector2(offset.size))
#
#         rect = pg.Rect(0, 0, 0, 0)
#         if type(currentOffset) == pg.Vector2:
#             rect = pg.Rect((0, 0), size - 2 * currentOffset)
#             rect.center = center
#         elif type(currentOffset) == pg.Rect:
#             rect = pg.Rect((currentOffset.x, currentOffset.w), (size.x - currentOffset.x - currentOffset.y,
#                                                                 size.y - currentOffset.w - currentOffset.h))
#
#         if shape == "rectangle":
#             pg.draw.rect(surf, colours[layer], rect, border_radius=radii[layer])
#         else:
#             pg.draw.ellipse(surf, colours[layer].value, rect)
#
#     offset = pg.Vector2(size)
#     offset.x *= offsetWidth
#     offset.y *= offsetHeight
#
#     if base:
#         self.base_surface.blit(surf, pos - offset)
#     else:
#         self.surface.blit(surf, pos - offset)


# new_array[np.int16(positions[0, :]), np.int16(positions[1, :]), :] = [0, 0, 0]
# new_surf = pg.surfarray.make_surface(new_array)
# new_surf.set_alpha()
# self.surface = new_surf

# def refresh(self):
#     self.size = pg.Vector2(self.base_surface.get_size())
#     self.surface = self.base_surface.copy()

# def clear_surfaces(self):
#     self.surface = None
#     self.base_surface = None
#     self.font = None

# def get_surface(self, image, pos=(0, 0), location=BlitLocation.topLeft):
#     imageRect = pg.Rect(pos, image.get_size())
#
#     if location == BlitLocation.centre:
#         imageRect.topleft = pg.Vector2(imageRect.topleft) - pg.Vector2(imageRect.size) / 2
#     elif location == BlitLocation.topRight:
#         imageRect.x -= imageRect.width
#
#     surf = pg.Surface(self.size, pg.SRCALPHA)
#     surf.blit(image, imageRect.topleft)
#
#     surfaceCopy = self.surface.copy()
#     surfaceCopy.blit(surf, (0, 0))
#
#     return surfaceCopy

# def scale_surface(self, scale, base=False):
#     self.size = pg.Vector2(self.base_surface.get_size()) * scale
#     self.surface = pg.transform.scale(self.surface, pg.Vector2(self.surface.get_size()) * scale)
#     if base:
#         self.base_surface = pg.transform.scale(self.base_surface, pg.Vector2(self.base_surface.get_size()) * scale)
class Screen:
    def __init__(self, size, font=None, colour=None):
        self.size = pg.Vector2(size)
        self.base_surface = pg.Surface(size, pg.SRCALPHA)
        self.surface = pg.Surface(size, pg.SRCALPHA)
        if font:
            self.fonts = Fonts()
            self.font: pg.font.Font = font
        else:
            self.fonts = Fonts()
            self.font = self.fonts.normal

        self.colour = colour
        if colour:
            self.base_surface.fill(colour)

    def add_surf(self, surf: pg.Surface, pos=(0, 0), base=False, location=BlitLocation.topLeft):
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

        if base:
            self.base_surface.blit(surf, surf_rect.topleft)
        else:
            self.surface.blit(surf, surf_rect.topleft)

    def update_pixels(self, pos, colour=Colours.black.value, base=False, width=2):
        pad = (2 * width - 1) / 2
        for x_pos in range(int(pos[0] - pad), int(pos[0] + 1 + pad)):
            for y_pos in range(int(pos[1] - pad), int(pos[1] + 1 + pad)):
                # if np.all(pos != np.array([x_pos, y_pos])):
                #     colour = pg.Color(colour.r, colour.g, colour.b, 0)
                # else:
                #     colour = pg.Color(colour.r, colour.g, colour.b, 255)

                if base:
                    # self.base_surface.set_at((x_pos, y_pos), colour)
                    pg.draw.circle(self.base_surface, colour, (x_pos, y_pos), 3, 2)
                    # self.window.blit(pg.transform.scale(self.window, self.window.get_rect().size), (0, 0))
                else:
                    # self.surface.set_at((x_pos, y_pos), colour)
                    pg.draw.circle(self.surface, colour, (x_pos, y_pos), 3, 2)
                    # self.window.blit(pg.transform.scale(self.window, self.window.get_rect().size), (0, 0))

    def refresh(self):
        self.size = pg.Vector2(self.base_surface.get_size())
        self.surface = self.base_surface.copy()


class SpiralTest():
    def __init__(self, amplitude, turns, size=(1200, 1200)):
        self.amplitude = amplitude
        self.turns = turns
        self.display_size = pg.Vector2(size)
        self.window = pg.display.set_mode(self.display_size)
        self.window.fill(Colours.white.value)

        self.screen = Screen(size)
        self.spiral_surface, self.target_coords = self.create_surface()
        self.screen.add_surf(self.spiral_surface, pg.Vector2(size) / 2, location=BlitLocation.centre, base=True)
        # self.screen.add_text("")
        self.screen.refresh()
        self.offset = np.array(self.display_size - self.spiral_surface.get_size()) / 2
        self.target_coords += np.asarray(self.offset, dtype=np.int16)

        self.window.blit(self.screen.surface, (0, 0))
        pg.display.flip()

        self.running = True

        self.spiral_data = np.zeros((5, 0))
        self.spiral_started = False
        self.coord_count = 0

    # def get_closest_coord(self, pos):
    #     i = self.coord_count
    #     distances = np.linalg.norm(self.target_coords - pos, axis=1)
    #     error = min(distances)
    #     close_coords = np.unique(self.target_coords[distances == error, :], axis=0)
    #     if np.array_equal(close_coords[0], self.target_coords[i]):
    #         return close_coords[0], error
    #     elif np.array_equal(close_coords[0], self.target_coords[i+1]):
    #         self.coord_count += 1
    #         return close_coords[0], error
    #     else:
    #         error = np.linalg.norm(self.target_coords[i] - pos)
    #         return self.target_coords[i], error

    def get_closest_coord(self, pos):
        i = self.coord_count
        print(pos)
        print(self.target_coords[i])
        pos_angle=(np.arctan2(pos[1], pos[0]))
        print("pos:",pos_angle)
        targ_angle=(np.arctan2(self.target_coords[i][1],self.target_coords[i][0]))
        print("trag:",targ_angle)

        error = np.linalg.norm(self.target_coords - pos, axis=1)
        if pos_angle<targ_angle:
            coord=self.target_coords[i]
            self.coord_count+=1
            return coord, error

        else:
            return self.target_coords[i],0

    def create_surface(self, size=(800, 800)):
        n = 500
        t = np.logspace (0,np.log10(2*np.pi), n)
        t=np.flip(2*np.pi-t)
        x = self.amplitude * t * np.cos(self.turns * t)
        y = self.amplitude * t * np.sin(self.turns * t)

        x -= np.min(x)
        y -= np.min(y)

        x_pixels = np.expand_dims(np.asarray(np.round((x / np.max(x)) * size[0]) - 1, dtype=np.int16), axis=1)
        y_pixels = np.expand_dims(np.asarray(np.round((y / np.max(y)) * size[1]) - 1, dtype=np.int16), axis=1)

        coords = np.concatenate([x_pixels, y_pixels], axis=1)
        midpoint = np.array(np.floor((size[0] - 1) / 2), dtype=np.int16)
        delta = (midpoint - coords[0, :]) * 2
        coords += delta

        spiral_screen = Screen(size + pg.Vector2(*delta), font=None)
        for pos in coords:
            spiral_screen.update_pixels(pos, base=True)

        return spiral_screen.base_surface, coords

    def create_dataframe(self):
        return pd.DataFrame(data=self.spiral_data.transpose(),
                            columns=["rel_pos_x", "rel_pos_y", "theta","error","time"])

    def loop(self):
        start_time = time.perf_counter()

        while self.running:
            for event in pg.event.get():
                # print(event.dict)
                if event.type == pg.MOUSEBUTTONDOWN and self.spiral_started == False:
                    rel_pos = pg.Vector2(pg.mouse.get_pos() - self.display_size / 2)
                    data = np.expand_dims([*rel_pos, np.arctan2(*rel_pos), 0, 0], axis=1)
                    self.spiral_data = np.append(self.spiral_data, data, axis=1)
                    start_time = time.perf_counter()
                    self.spiral_started = True

                elif event.type == pg.MOUSEMOTION and self.spiral_started:
                    pos = pg.mouse.get_pos()
                    rel_pos = pg.Vector2(pos - self.display_size / 2)

                    coord, error = self.get_closest_coord(np.array(rel_pos))
                    data = np.expand_dims([*rel_pos, np.arctan2(*rel_pos), error, time.perf_counter() - start_time],
                                          axis=1)
                    self.spiral_data = np.append(self.spiral_data, data, axis=1)
                    self.screen.refresh()
                    self.screen.update_pixels(coord, colour=pg.Color(255, 0, 0), base=True)
                    # optionally add blue line to show actual location
                    self.screen.update_pixels(pos, colour=pg.Color(0, 0, 255))

                    self.window.blit(self.screen.surface, (0, 0))
                    pg.display.flip()

                elif event.type == pg.MOUSEBUTTONUP:
                    self.running = False
                    time.sleep(1)
                    return self.spiral_data

                elif event.type == pg.QUIT:
                    self.running = False


if __name__ == "__main__":
    os.chdir('/Users/Thinkpad/Desktop/Warwick/hero-monitor')

    pg.init()
    spiral_test = SpiralTest(2, 3, (1000, 1000))
    spiral_test.loop()  # optionally extract data from here as array
    spiral_data = spiral_test.create_dataframe()
    spiral_data.to_csv('spiraldata.csv', index=False)
    print(spiral_data.head(10))



