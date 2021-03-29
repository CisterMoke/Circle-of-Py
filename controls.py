from menu import Menu
from game import Game
import pygame as pg
from math import atan2, degrees


def menu_controls(event: pg.event.Event, menu: Menu):
    if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
        menu.click_at(event.pos[0], event.pos[1])


rotate = False
shifts = []


def game_controls(event: pg.event.Event, game: Game):
    if game.paused:
        return
    global rotate, shifts
    if event.type == pg.KEYDOWN and event.key == pg.K_LCTRL:
        rotate = True
    if event.type == pg.KEYUP and event.key == pg.K_LCTRL:
        rotate = False
    if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
        game.grab_at(event.pos[0], event.pos[1])
        for card in game.grabbed:
            rel_x = event.pos[0] - card.center[0]
            rel_y = -event.pos[1] + card.center[1]
            shifts.append(degrees(atan2(rel_y, rel_x)))
    if event.type == pg.MOUSEBUTTONUP and event.button == 1:
        game.release()
    if event.type == pg.MOUSEMOTION:
        if rotate:
            for num, card in enumerate(game.grabbed):
                rel_x = event.pos[0] - card.center[0]
                rel_y = -event.pos[1] + card.center[1]
                angle = degrees(atan2(rel_y, rel_x))
                card.spin(angle - shifts[num])
                shifts[num] = angle
        else:
            for card in game.grabbed:
                card.move(event.rel)


def reset_states():
    global rotate
    rotate = False
