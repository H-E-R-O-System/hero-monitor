from consultation.screen import Screen, Colours, BlitLocation
import numpy as np
import pygame as pg
import time
import pandas as pd
import os


class SpiralTest:
    def __init__(self, size=(600, 600)):
        self.display_size = pg.Vector2(size)
        self.window = pg.display.set_mode(self.display_size)
        self.window.fill(Colours.white.value)

        self.screen = Screen(size)
        self.spiral_surface, self.target_coords = self.create_surface()
        self.screen.add_surf(self.spiral_surface, pg.Vector2(size) / 2, location=BlitLocation.centre, base=True)
        self.screen.refresh()

        self.offset = np.array(self.display_size - self.spiral_surface.get_size()) / 2
        self.target_coords += np.asarray(self.offset, dtype=np.int16)

        self.window.blit(self.screen.surface, (0, 0))
        pg.display.flip()

        self.running = True

        self.spiral_data = np.zeros((4, 0))
        self.spiral_started = False

    def get_closest_coord(self, pos):

        distances = np.linalg.norm(self.target_coords - pos, axis=1)
        close_coords = np.unique(self.target_coords[distances == min(distances), :], axis=0)
        return close_coords

    def create_surface(self, A=1, B=2.2, n=10000, size=(500, 500)):
        t = np.linspace(0, 2 * np.pi, n)
        x = A * t * np.cos(B * t)
        y = A * t * np.sin(B * t)

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
        return pd.DataFrame(data=self.spiral_data.transpose(), columns=["rel_pos_x", "rel_pos_y", "theta", "time"])

    def loop(self):
        start_time = time.monotonic()

        while self.running:
            for event in pg.event.get():
                # print(event.dict)
                if event.type == pg.MOUSEBUTTONDOWN:
                    rel_pos = pg.Vector2(pg.mouse.get_pos() - self.display_size / 2)
                    data = np.expand_dims([*rel_pos, np.arctan2(*rel_pos), 0], axis=1)

                    self.spiral_data = np.append(self.spiral_data, data, axis=1)
                    start_time = time.monotonic()
                    self.spiral_started = True

                elif event.type == pg.MOUSEMOTION and self.spiral_started:
                    pos = pg.mouse.get_pos()
                    rel_pos = pg.Vector2(pos - self.display_size/2)
                    data = np.expand_dims([*rel_pos, np.arctan2(*rel_pos), time.monotonic() - start_time], axis=1)
                    self.spiral_data = np.append(self.spiral_data, data, axis=1)

                    for coord in self.get_closest_coord(np.array(pos)):
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
    os.chdir('/Users/benhoskings/Documents/Projects/hero-monitor')
    # os.chdir('/Users/benhoskings/Documents/Pycharm/Hero_Monitor')

    pg.init()
    spiral_test = SpiralTest()
    spiral_test.loop()  # optionally extract data from here as array
    spiral_data = spiral_test.create_dataframe()
    print(spiral_data.head(20))
