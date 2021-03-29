import pygame as pg
import parallel as par
from card import Card
from config import ASPECT, PROC_POOL
from typing import List, Tuple
from tools import circle_points, CardState


class Game:
    def __init__(self, cards=None):
        self.cards: pg.sprite.RenderUpdates = pg.sprite.RenderUpdates()
        if cards is not None:
            sprites = (self.cards.add(card) for card in cards)

        self.over = False
        self.grabbed: List[Card] = []
        self.paused = False
        # self.selected: List[Card] = []

    def grab_at(self, x, y):
        for card in self.cards:
            if card.rect.collidepoint(x, y):
                self.grabbed.append(card)
                break

    def drag(self, disp: Tuple[float, float]):
        for card in self.grabbed:
            card.move(disp)

    def release(self):
        for card in self.grabbed:
            card.release()
        self.grabbed = []

    def spawn_at(self, card_num=1, x=ASPECT[0]//2, y=ASPECT[1]//2, angle=0):
        card = Card(card_num, (x, y))
        card.rotate(angle)
        self.cards.add(card)

    def pause(self):
        self.paused = True

    def resume(self):
        self.paused = False

    def finish(self):
        self.over = True

    def update(self):
        self.cards.update()
        for grabbed in self.grabbed:
            dots = []
            dvs = []
            collides = {c.__hash__(): c for c in pg.sprite.spritecollide(grabbed, self.cards, False)
                        if c not in self.grabbed}
            pair_list = [(grabbed.to_dict(), card.to_dict()) for card in collides.values()]
            futures = par.interact(pair_list, PROC_POOL)
            for f in futures:
                r1, r2, contacts, forces = f.result()
                if collides[r2["hash"]].state == CardState.GRABBED or contacts is None:
                    continue
                for trans, torque in r2["forces"]:
                    collides[r2["hash"]].apply_forces(trans, torque)
                dots += contacts
                dvs += forces


class CircleGame(Game):
    def __init__(self):
        super().__init__()
        num_cards = 54
        radius = 20
        center = (ASPECT[0]//2, ASPECT[1]//2)
        c_points = circle_points(num_cards, radius, center)
        for i, p in enumerate(c_points):
            self.spawn_at(i+1, p[0], p[1], p[2]+90)
