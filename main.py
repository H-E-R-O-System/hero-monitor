import os

import pygame as pg

from consult import Consultation

os.environ['SDL_VIDEO_WINDOW_POS'] = "0,0"
pg.init()
consult = Consultation()
consult.loop()