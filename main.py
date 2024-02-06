from consult import Consultation
import os
import pygame as pg

os.environ['SDL_VIDEO_WINDOW_POS'] = "0,0"
pg.init()
consult = Consultation()
consult.loop()