import pygame as pg
from config import ASPECT

pg.init()
pg.display.init()
pg.display.set_mode((50, 100))
running = True
while running:
    for event in pg.event.get():
        print(event, event.type)
        if event.type == pg.QUIT:
            running = False
            break
pg.quit()
