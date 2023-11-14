import enum

import pygame as pg


class Colours(enum.Enum):
    clear = pg.SRCALPHA
    white = pg.Color(255, 255, 255)
    black = pg.Color(1, 1, 1)
    darkGrey = pg.Color(60, 60, 60)
    lightGrey = pg.Color(200, 200, 200)
    green = pg.Color(100, 255, 100)
    red = pg.Color(255, 100, 100)
    shadow = pg.Color(180, 180, 180)
