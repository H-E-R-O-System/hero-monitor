import math
import os

import pandas as pd
import pygame as pg


def createSheet(baseDir, spriteSize, perRow, gridWidth=0, path=None):
    files = os.listdir(baseDir)
    print(files)
    # images 80x80
    surfLength = math.floor(len(files) / (perRow)) + 1
    print(surfLength)
    sheet = pg.Surface((spriteSize.x * perRow + ((perRow + 1) * gridWidth),
                        spriteSize.y * surfLength + ((surfLength + 1) * gridWidth)), pg.SRCALPHA)

    if gridWidth != 0:
        for idx in range(perRow + 1):
            pg.draw.line(sheet, pg.Color(50, 50, 200), (2 + idx * (gridWidth + spriteSize.x), 0),
                         (2 + idx * (gridWidth + spriteSize.x), sheet.get_size()[0]), width=gridWidth)

        for idx in range(surfLength + 1):
            pg.draw.line(sheet, pg.Color(50, 50, 200), (0, 2 + idx * (gridWidth + spriteSize.y)),
                         (sheet.get_size()[0], 2 + idx * (gridWidth + spriteSize.y)), width=gridWidth)

    for idx, name in enumerate(files):
        img = pg.image.load(os.path.join(baseDir, name))

        pos = pg.Vector2((idx % perRow) * spriteSize.x + (gridWidth * ((idx % perRow) + 1)),
                                 (math.floor(idx / perRow) * (spriteSize.y + gridWidth)) * 2 + gridWidth)
        sheet.blit(img, pos)

    if path:
        pg.image.save(sheet, path)


createSheet("sprites/mouth", pg.Vector2(64, 64), 8, 5, "mouth_sprites.png")
