import numpy as np
import pygame as pg
import time
import pandas as pd
import os
import gtts
import time

from consultation.screen import Screen, Colours, BlitLocation
from consultation.display_screen import DisplayScreen

import matplotlib.pyplot as plt


class SpiralTest:
    def __init__(self, amplitude, turns, size=(1200, 1200), parent=None):
        self.parent = parent
        self.amplitude = amplitude
        self.turns = turns

        if parent is not None:
            self.display_size = parent.display_size
            self.bottom_screen = parent.bottom_screen
            self.top_screen = parent.top_screen
        else:
            self.display_size = pg.Vector2(size)
            self.bottom_screen = pg.display.set_mode(self.display_size)
            self.top_screen = None

        self.display_screen = DisplayScreen(self.display_size)
        if parent:
            self.display_screen.avatar.face_colour = parent.display_screen.avatar.face_colour
            self.display_screen.avatar.update_colours()

        self.touch_screen = Screen(size, colour=Colours.white)

        self.spiral_surface, self.target_coords, self.coords_polar = self.create_surface()
        self.touch_screen.add_surf(self.spiral_surface, pg.Vector2(size) / 2, location=BlitLocation.centre, base=True)
        self.touch_screen.refresh()
        self.offset = np.array(self.touch_screen.size - self.spiral_surface.get_size()) / 2
        self.target_coords += np.asarray(self.offset, dtype=np.int16)

        self.running = True

        self.spiral_data = np.zeros((5, 0))
        self.spiral_started = False
        self.coord_count = 0

    def update_display(self):
        if self.top_screen is not None:
            self.top_screen.blit(self.display_screen.get_surface(), (0, 0))
        self.bottom_screen.blit(self.touch_screen.get_surface(), ((self.display_size.x - self.touch_screen.size.x) / 2, 0))
        pg.display.flip()

    def ask_question(self, text):

        self.display_screen.instruction = None
        self.display_screen.update()

        self.question_audio = gtts.gTTS(text=text, lang='en', slow=False)
        question_audio_file = f'consultation/question_audio/tempsave_question_spiral.mp3'
        self.question_audio.save(question_audio_file)

        pg.mixer.music.load(question_audio_file)
        pg.mixer.music.play()

        # Keep in idle loop while speaking
        self.display_screen.avatar.state = 1
        start = time.monotonic()
        while pg.mixer.music.get_busy():
            if time.monotonic() - start > 0.15:
                self.display_screen.update()
                self.update_display()
                self.display_screen.avatar.speak_state = (self.display_screen.avatar.speak_state + 1) % 2
                start = time.monotonic()

        self.display_screen.avatar.state = 0

        self.display_screen.update()
        self.update_display()

    def get_closest_coord(self, pos):
        pos_polar= pos - self.touch_screen.size / 2
        i = self.coord_count
        pos_angle=(np.arctan2(pos_polar[1], pos_polar[0]))
        targ_angle=(np.arctan2(self.coords_polar[i][1],self.coords_polar[i][0]))

        error = np.linalg.norm(self.target_coords[i] - pos, axis=0)
        if pos_angle>targ_angle:
            coord=self.target_coords[i]
            self.coord_count+=1
            return coord, error

        else:
            return self.target_coords[i],0

    def create_surface(self, size=(800, 800)):
        n = 600
        t = np.logspace (0,np.log10(2*np.pi), n)
        t=np.flip(2*np.pi-t)
        x = self.amplitude * t * np.cos(self.turns * t)
        y = self.amplitude * t * np.sin(self.turns * t)

        x_polar = x+np.min(x)
        y_polar = y+np.min(y)
        x_pixels = np.expand_dims(np.asarray(np.round((x_polar / np.max(x)) * size[0]) - 1, dtype=np.int16), axis=1)
        y_pixels = np.expand_dims(np.asarray(np.round((y_polar / np.max(y)) * size[1]) - 1, dtype=np.int16), axis=1)

        coords = np.concatenate([x_pixels, y_pixels], axis=1)
        coords_polar = np.concatenate([np.expand_dims(x, axis=1), np.expand_dims(y, axis=1)], axis=1)
        midpoint = np.array(np.floor((size[0] - 1) / 2), dtype=np.int16)
        delta = (midpoint - coords[0, :]) * 2
        coords += delta
        # print(coords_polar)

        spiral_screen = pg.Surface(size + pg.Vector2(*delta))
        spiral_screen.fill(Colours.white.value)
        for pos in coords:
            pg.draw.circle(spiral_screen, center=pos, color=Colours.black.value, radius=5)
            # spiral_screen.update_pixels(pos, base=True)

        return spiral_screen, coords , coords_polar

    def create_surface_2(self, size=(550, 550)):
        n = 500
        a, b, n = 0, 0.5, 5
        theta = np.logspace(0, np.log10(2 * np.pi), n)
        x = (a+b*theta) * np.cos(t)
        y = (a+b*theta) * np.sin(self.turns * t)
        print(x.shape)
        points = np.array(([x, y])).transpose()

        fig, ax = plt.subplots()
        plt.grid(True)

        ax.plot(x, y)

        plt.show()

        print(points.shape)

    def create_dataframe(self):
        return pd.DataFrame(data=self.spiral_data.transpose(),
                            columns=["rel_pos_x", "rel_pos_y", "theta","error","time"])

    def get_relative_mose_pos(self):
        if self.parent is None:
            return pg.Vector2(pg.mouse.get_pos()) - pg.Vector2((self.display_size.x - self.touch_screen.size.x) / 2,
                                                               0)
        else:
            return pg.Vector2(pg.mouse.get_pos()) - pg.Vector2((self.display_size.x - self.touch_screen.size.x) / 2, self.display_size.y)

    def entry_sequence(self):
        self.update_display()
        if self.parent:
            self.parent.speak_text("Please trace the spiral, starting from the center")

    def exit_sequence(self):
        self.update_display()
        if self.parent:
            self.parent.speak_text("Thank you for completing the spiral test")

    def loop(self):
        self.entry_sequence()
        start_time = time.perf_counter()

        while self.running:
            for event in pg.event.get():
                # print(event.dict)
                if event.type == pg.MOUSEBUTTONDOWN and not self.spiral_started:
                    rel_pos = pg.Vector2(self.get_relative_mose_pos() - self.touch_screen.size / 2)

                    data = np.expand_dims([*rel_pos, np.arctan2(*rel_pos), 0, 0], axis=1)
                    self.spiral_data = np.append(self.spiral_data, data, axis=1)
                    start_time = time.perf_counter()
                    self.spiral_started = True

                elif event.type == pg.MOUSEMOTION and self.spiral_started:
                    pos = self.get_relative_mose_pos()
                    rel_pos = pg.Vector2(pos - self.touch_screen.size / 2)

                    coord, error = self.get_closest_coord(np.array(pos))
                    data = np.expand_dims([*rel_pos, np.arctan2(*rel_pos), error, time.perf_counter() - start_time],
                                          axis=1)
                    self.spiral_data = np.append(self.spiral_data, data, axis=1)

                    self.touch_screen.refresh()
                    pg.draw.circle(self.touch_screen.base_surface, center=coord, color=Colours.red.value, radius=5)
                    pg.draw.circle(self.touch_screen.base_surface, center=pos, color=Colours.blue.value, radius=5)

                    self.update_display()

                elif event.type == pg.MOUSEBUTTONUP:
                    self.running = False

                elif event.type == pg.QUIT:
                    self.running = False

        self.exit_sequence()


if __name__ == "__main__":
    # os.chdir('/Users/Thinkpad/Desktop/Warwick/hero-monitor')
    os.chdir("/Users/benhoskings/Documents/Pycharm/Hero_Monitor")

    pg.init()
    spiral_test = SpiralTest(0.8, 5, (600, 600))
    spiral_test.create_surface_2()
    # spiral_test.loop()  # optionally extract data from here as array
    # spiral_data = spiral_test.create_dataframe()
    # spiral_data.to_csv('spiraldata.csv', index=False)
    # print(spiral_data.head(5))
