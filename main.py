import pygame as pg
from card import Card
from typing import Optional
import physics as ph
from tools import circle_points
from random import shuffle


ASPECT = (1200, 720)
FPS = 60
BGD = (0, 150, 0)

# Init screen
pg.init()
pg.font.init()
pg.display.set_caption("Circle of death")
screen = pg.display.set_mode(ASPECT)
background = pg.Surface(ASPECT)
background.fill(BGD)
clock = pg.time.Clock()
font = pg.font.SysFont("Calibri", 30)
circle_cards = pg.sprite.Group()
picked_cards = pg.sprite.Group()

# Init cards
num_cards = 54
radius = 200
center = (ASPECT[0]//2, ASPECT[1]//2)
c_points = circle_points(num_cards, radius, center)
card_nums = list(range(1, num_cards+1))
shuffle(card_nums)
card_list = []
for i, p in enumerate(c_points):
    card = Card(card_nums[i], p[0:2])
    card.rotate(p[2]+90)
    card_list.append(card)
    circle_cards.add(card)

running = True
grabbed: Optional[Card] = None
debug_card: Optional[Card] = None
interactions = []

# Main loop
while running:
    clock.tick(FPS)
    for event in pg.event.get():
        running = False if event.type == pg.QUIT else True
        if event.type == pg.MOUSEBUTTONDOWN:
            if event.button == 1:
                if grabbed is not None:
                    grabbed.release()
                    grabbed = None
                else:
                    for sprite in circle_cards.sprites():
                        sprite: Card
                        if sprite.rect.collidepoint(event.pos[0], event.pos[1]):
                            sprite.grab()
                            grabbed = sprite
                            break
            if event.button == 3:
                if grabbed is not None:
                    grabbed.flip()

        if event.type == pg.MOUSEMOTION:
            if grabbed is not None:
                grabbed.move(event.rel)
        if event.type == pg.MOUSEWHEEL:
            if grabbed is not None:
                grabbed.spin(event.y * 5)

    debug_card = grabbed if grabbed is not None else debug_card
    circle_cards.update()

    dots = []
    dvs = []
    near_idx = []
    if grabbed is not None:
        near_idx = grabbed.rect.collidelistall(card_list)
    for i in near_idx:
        if card_list[i] == grabbed:
            continue
        contacts, forces = grabbed.interact(card_list[i])
        dots += contacts
        dvs += forces

    screen.blit(background, background.get_rect())
    circle_cards.draw(screen)
    # debug_text = ("({:0.3f}, {:0.3f}), ({:0.3f}, {:0.3f}), {:0.3f}, {:0.3f}, {}"
    #               .format(*debug_card.velocity, *debug_card.delta_v, debug_card.omega, debug_card.delta_omega, debug_card.state)
    #               if debug_card is not None else "")
    # debug = font.render(debug_text, False, (255, 255, 255))
    # for dot, force in zip(dots, dvs):
    #     pg.draw.line(screen, (0, 0, 255), dot, ph.add([dot, ph.mul(force, 10)]), 3)
    # screen.blit(debug, (0, 0))
    # hbox = [pg.Rect((x-3, y-3), (6, 6)) for x, y in dots]
    # surf = pg.Surface((5, 5))
    # surf.fill((255, 0, 0))
    # for c in card_list:
    #     h = c.hitbox
    #     corners = h.get_rotated(c.angle)
    #     for x, y in corners:
    #         rect = pg.Rect((x-3, y-3), (6, 6))
    #         hbox.append(rect)
    # for rect in hbox:
    #     screen.blit(surf, rect)
    pg.display.update()


pg.quit()

