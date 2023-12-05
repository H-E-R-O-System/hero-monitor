import pygame as pg
from consultation.screen import Screen, BlitLocation, Colours

pg.init()

window = pg.display.set_mode((1024, 1200))
top_surf = window.subsurface((0, 0, 1024, 600))
bottom_surf = window.subsurface((0, 600, 1024, 600))
top_surf.fill((255, 255, 255))
bottom_surf.fill((200, 200, 200))
pg.display.update()
running = True
draw_start = False

while running:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
            pg.quit()
        elif event.type == pg.MOUSEBUTTONDOWN:
            print("Mouse")
            draw_start = True

        elif event.type == pg.MOUSEMOTION and draw_start:
            draw_pos = pg.mouse.get_pos() - pg.Vector2(0, 600)
            top_surf.set_at((int(draw_pos.x), int(draw_pos.y)), Colours.red.value)
            pg.display.update()

        elif event.type == pg.MOUSEBUTTONUP:
            draw_start = False
