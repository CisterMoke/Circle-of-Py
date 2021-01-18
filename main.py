from multiprocessing import freeze_support


def pool_init():
    return 1


def main():
    import pygame as pg
    from typing import Optional
    from tools import circle_points
    from random import shuffle
    import parallel as par
    import concurrent.futures as cf

    ASPECT = (1200, 720)
    FPS = 60
    BGD = (0, 150, 0)
    proc_pool = cf.ProcessPoolExecutor()
    par.init_pool(proc_pool)

    # Init screen
    pg.init()
    pg.font.init()
    pg.display.init()
    pg.display.set_caption("Circle of Py")
    screen = pg.display.set_mode(ASPECT)
    background = pg.Surface(ASPECT)
    background.fill(BGD)
    clock = pg.time.Clock()
    font = pg.font.SysFont("Calibri", 30)
    circle_cards = pg.sprite.RenderUpdates()
    moving_cards = pg.sprite.RenderUpdates()
    picked_cards = pg.sprite.Group()

    from card import Card, CardState

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

    # Draw background
    screen.blit(background, background.get_rect())
    circle_cards.draw(screen)
    pg.display.update()

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

        moving_cards.empty()
        for card in card_list:
            if card.state != CardState.REST:
                moving_cards.add(card)

        dots = []
        dvs = []
        if grabbed is not None:
            collides = {c.__hash__(): c for c in pg.sprite.spritecollide(grabbed, circle_cards, False)}
            pair_list = [(grabbed.to_dict(), card.to_dict()) for card in collides.values()]
            futures = par.interact(pair_list, proc_pool)
            for f in futures:
                r1, r2, contacts, forces = f.result()
                if collides[r2["hash"]].state == CardState.GRABBED or contacts is None:
                    continue
                # collides[c1["hash"]].apply_forces(c1.get("trans", (0, 0)), c1.get("torque", 0))
                for trans, torque in r2["forces"]:
                    collides[r2["hash"]].apply_forces(trans, torque)
                dots += contacts
                dvs += forces
                # future = thread.submit(grabbed.interact, card)
                # contacts, forces = future.result()
                # contacts, forces = grabbed.interact(card)
                # dots += contacts
                # dvs += forces

        #     near_idx = grabbed.rect.collidelistall(card_list)
        # for i in near_idx:
        #     if card_list[i] == grabbed:
        #         continue
        #     future = thread.submit(grabbed.interact, card_list[i])
        #     contacts, forces = future.result()
        #     dots += contacts
        #     dvs += forces

        circle_cards.clear(screen, background)
        updates = circle_cards.draw(screen)
        fps = font.render(str(int(clock.get_fps())), False, (255, 255, 255))
        fps_rect = fps.get_rect()
        screen.blit(background, (0, 0), fps_rect)
        screen.blit(fps, (0, 0), fps_rect)
        updates.append(fps.get_rect())
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
        pg.display.update(updates)
    pg.quit()
    proc_pool.shutdown()


if __name__ == '__main__':
    freeze_support()
    main()

