import pygame as pg
from card import Card, CardState
from typing import Optional
import physics as ph


ASPECT = (800, 600)
FPS = 60
BGD = (0, 150, 0)

pg.init()
pg.font.init()
pg.display.set_caption("Circle of death")
screen = pg.display.set_mode(ASPECT)
background = pg.Surface(ASPECT)
background.fill(BGD)
clock = pg.time.Clock()
font = pg.font.SysFont("Calibri", 30)

ace = Card(1, (ASPECT[0]/2, ASPECT[1]/2))
joker = Card(53, (ASPECT[0]/3, ASPECT[1]/2))
card_list = [ace, joker]
all_sprites = pg.sprite.Group()
all_sprites.add(ace)
all_sprites.add(joker)

running = True
grabbed: Optional[Card] = None
debug_card: Optional[Card] = None
interactions = []

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
                    for sprite in all_sprites.sprites():
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
    all_sprites.update()

    dots = []
    dvs = []
    for i in range(0, len(card_list)-1):
        if card_list[i+1].can_rest() and card_list[i].can_rest():
            continue
        near_idx = card_list[i].rect.collidelistall(card_list[i+1:])
        for idx in near_idx:
            contacts, forces = card_list[i].interact(card_list[i+idx+1])
            dots += contacts
            dvs += forces

    screen.blit(background, background.get_rect())
    all_sprites.draw(screen)
    debug_text = ("({:0.3f}, {:0.3f}), ({:0.3f}, {:0.3f}), {:0.3f}, {:0.3f}, {}"
                  .format(*debug_card.velocity, *debug_card.delta_v, debug_card.omega, debug_card.delta_omega, debug_card.state)
                  if debug_card is not None else "")
    debug = font.render(debug_text, False, (255, 255, 255))
    for dot, force in zip(dots, dvs):
        pg.draw.line(screen, (0, 0, 255), dot, ph.add([dot, ph.mul(force, 10)]), 3)
    screen.blit(debug, (0, 0))
    hbox = [pg.Rect((x-3, y-3), (6, 6)) for x, y in dots]
    surf = pg.Surface((5, 5))
    surf.fill((255, 0, 0))
    for c in card_list:
        h = c.hitbox
        corners = h.get_rotated(c.angle)
        for x, y in corners:
            rect = pg.Rect((x-3, y-3), (6, 6))
            hbox.append(rect)
    for rect in hbox:
        screen.blit(surf, rect)
    pg.display.update()


pg.quit()

