from consultation.screen import Screen, Colours, BlitLocation
import pygame as pg
import os
from typing import (
    Any,
    Callable,
    Dict,
    Generic,
    Iterable,
    Iterator,
    List,
    Literal,
    Optional,
    SupportsFloat,
    Tuple,
    TypeVar,
    Union,
)






if __name__ == "__main__":
    # os.chdir('/Users/benhoskings/Documents/Projects/hero-monitor')
    os.chdir("/Users/benhoskings/Documents/Pycharm/Hero_Monitor")
    pg.init()
    window = pg.display.set_mode(pg.Vector2(1024, 600))
    touch_screen = TouchScreen(pg.Vector2(window.get_size()))

    window.blit(touch_screen.screen.get_surface(sprites=True), (0, 0))
    pg.display.update()

    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                quit()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_q:
                    touch_screen.screen.refresh()
                elif event.key == pg.K_f:
                    window.blit(touch_screen.screen.get_surface(sprites=True), (0, 0))
                    pg.display.update()
                elif event.key == pg.K_1:
                    ...

                window.blit(touch_screen.screen.surface, (0, 0))
                pg.display.update()

            if event.type == pg.MOUSEBUTTONDOWN:
                touch_screen.click_test(pg.mouse.get_pos())