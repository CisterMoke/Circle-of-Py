import pygame as pg
from hitbox import Hitbox
import physics as ph
from tools import CardState


def card_num_suit_value(card_num):
    if card_num > 54 or card_num < 1:
        raise ValueError("Invalid card number")
    if card_num == 54:
        return "red", "joker"
    if card_num == 53:
        return "black", "joker"

    suits = ["spades", "diamonds", "clubs", "hearts"]
    faces = {1: "ace",
             11: "jack",
             12: "queen",
             13: "king"}
    suit = suits.pop(0)
    while card_num > 13:
        suit = suits.pop(0)
        card_num -= 13
    value = faces.get(card_num, card_num)
    return suit, value


def card_num_img(card_num):
    suit, value = card_num_suit_value(card_num)
    if value == "joker":
        filename = "{s}_{v}.png"
    else:
        filename = "{v}_of_{s}.png"
    return pg.image.load("cards/"+filename.format(v=value, s=suit)).convert_alpha()


CARD_SIZE = (100, 145)
CARD_IMG = {k: pg.transform.smoothscale(card_num_img(k), CARD_SIZE) for k in range(1, 55)}
CARD_IMG[0] = pg.transform.smoothscale(pg.image.load("cards/back.png").convert_alpha(), CARD_SIZE)


class Card(pg.sprite.Sprite):
    def __init__(self, card_num=1, center=(0, 0)):
        pg.sprite.Sprite.__init__(self)
        self.front: pg.surface.Surface = CARD_IMG[card_num]
        self.back: pg.surface.Surface = CARD_IMG[0]
        self.face_img = [self.back, self.front]
        self.face = 0

        self.num = card_num
        self.suit, self.value = card_num_suit_value(card_num)
        self.center = center
        self.angle = 0
        self.velocity = (0, 0)
        self.delta_v = (0, 0)
        self.omega = 0
        self.delta_omega = 0
        self.inertia = (CARD_SIZE[0]**2 + CARD_SIZE[1]**2)/120

        self.image = self.get_face()
        self.rect: pg.rect.Rect = self.image.get_rect(center=self.center)
        self.state: CardState = CardState.REST
        self.hitbox: Hitbox = Hitbox(self.center[0]-CARD_SIZE[0]//2, self.center[1]-CARD_SIZE[1]//2,
                             self.center[0]+CARD_SIZE[0]//2, self.center[1]+CARD_SIZE[1]//2)

    def to_dict(self):
        return {
            "hash": self.__hash__(),
            "hitbox": self.hitbox,
            "angle": self.angle,
            "area": CARD_SIZE[0] * CARD_SIZE[1],
            "center": self.center,
            "velocity": self.velocity,
            "omega": self.omega,
            "state": self.state,
            "inertia": self.inertia
        }

    def get_face(self):
        return self.face_img[self.face]

    def flip(self):
        self.face = (self.face + 1) % 2
        self.image = self.get_face()
        self.rotate(0)

    def rotate(self, theta):
        self.angle = (self.angle + theta) % 360
        self.image = pg.transform.rotate(self.get_face(), self.angle)
        self.rect = self.image.get_rect(center=self.center)

    def spin(self, angle):
        self.omega = angle
        self.rotate(angle)
        self.state = CardState.MOVED

    def translate(self, disp):
        self.center = (self.center[0] + disp[0], self.center[1] + disp[1])
        self.rect.center = self.center
        self.hitbox.translate(disp)

    def move(self, disp):
        self.velocity = disp
        self.translate(disp)
        self.state = CardState.MOVED

    def grab(self):
        self.state = CardState.GRABBED

    def release(self):
        self.state = CardState.RELEASED

    def rest(self):
        self.velocity = self.delta_v = (0, 0)
        self.omega = self.delta_omega = 0

    def can_rest(self):
        return ((self.velocity[0]**2 + self.velocity[1]**2 < 0.01)
                and (self.delta_v[0]**2 + self.delta_v[1]**2 < 0.01)
                and -0.05 < self.omega < 0.05
                and -0.05 < self.delta_omega < 0.05)

    def update(self):
        if self.state == CardState.GRABBED:
            self.rest()

        if self.state == CardState.RELEASED:
            self.state = CardState.MOVING

        if self.state == CardState.MOVED:
            self.state = CardState.GRABBED

        if self.state == CardState.MOVING:
            if self.can_rest():
                self.rest()
                self.state = CardState.REST
            else:
                self.apply_physics()

    def update_velocities(self):
        self.velocity =(self.velocity[0] + self.delta_v[0], self.velocity[1] + self.delta_v[1])
        self.omega += self.delta_omega
        self.delta_v = (0, 0)
        self.delta_omega = 0

    def apply_forces(self, trans, torque):
        self.delta_v = (self.delta_v[0] + trans[0], self.delta_v[1] + trans[1])
        self.delta_omega += torque
        self.state = CardState.MOVING

    def apply_fric_force(self):
        v = (-self.velocity[0], -self.velocity[1])
        fric_trans = ph.get_fric_force(v, 1, 0, ph.MU_VEL)
        fric_trans = v if ph.bigger_norm(fric_trans, v) else fric_trans

        fric_rot = ph.get_rot_fric_force(-self.omega, ph.MU_OMEGA)
        fric_rot = -self.omega if abs(self.omega) < abs(fric_rot) else fric_rot
        self.apply_forces(fric_trans, fric_rot)

    def apply_physics(self):
        if self.state != CardState.MOVING:
            return

        self.update_velocities()
        self.translate(self.velocity)
        self.rotate(self.omega)
        self.apply_fric_force()
