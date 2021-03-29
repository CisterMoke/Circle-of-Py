from multiprocessing import freeze_support


def main():
    import pygame as pg
    import parallel as par
    from typing import Optional, Dict
    from config import ASPECT, FPS, BGD, PROC_POOL, MENU_FONT

    # Init screen
    pg.init()
    pg.font.init()
    pg.display.init()
    pg.display.set_caption("Circle of Py")
    screen = pg.display.set_mode(ASPECT)
    background = pg.Surface(ASPECT)
    background.fill(BGD)
    font = pg.font.SysFont(*MENU_FONT)
    clock = pg.time.Clock()

    import controls
    from menu import MainMenu, PauseMenu, Menu
    from game import CircleGame, Game

    par.init_pool(PROC_POOL)

    MENU: Dict[str, Menu] = {"main": MainMenu(),
                             "pause": PauseMenu()}

    def close():
        nonlocal running
        running = False
        pg.quit()
        PROC_POOL.shutdown()
        return "QUIT"

    def play():
        nonlocal curr_game, curr_menu
        curr_game = CircleGame()
        screen.blit(background, background.get_rect())
        pg.display.update()
        curr_menu = None

    def resume():
        nonlocal curr_game, curr_menu
        curr_game.resume()
        screen.blit(background, background.get_rect())
        pg.display.update()
        curr_menu = None

    def quit_game():
        nonlocal curr_game, curr_menu
        curr_game.finish()
        curr_game.cards.clear(screen, background)
        curr_game = None
        screen.blit(background, background.get_rect())
        curr_menu = MENU["main"]
        curr_menu.draw()
        pg.display.update()

    MENU["main"].curr_screen.buttons["play"].action = play
    MENU["main"].curr_screen.buttons["quit"].action = close
    MENU["pause"].curr_screen.buttons["resume"].action = resume
    MENU["pause"].curr_screen.buttons["quit"].action = quit_game

    curr_menu: Optional[Menu] = MENU["main"]
    curr_game: Optional[Game] = None
    running = True

    screen.blit(background, background.get_rect())
    curr_menu.draw()
    pg.display.update()

    # Main loop
    while running:
        clock.tick(FPS)

        # Controls
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
                break
            if curr_menu:
                controls.menu_controls(event, curr_menu)
            elif curr_game:
                if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                    curr_game.pause()
                    curr_menu = MENU["pause"]
                    curr_menu.draw()
                    pg.display.update()
                else:
                    controls.game_controls(event, curr_game)
        if not running:
            break

        updates = []
        if curr_game and not curr_menu:
            curr_game.update()
            curr_game.cards.clear(screen, background)
            updates += curr_game.cards.draw(screen)


        #     running = False if event.type == pg.QUIT else True
        #     if event.type == pg.MOUSEBUTTONDOWN:
        #         if event.button == 1:
        #             if grabbed is not None:
        #                 grabbed.release()
        #                 grabbed = None
        #             else:
        #                 for sprite in circle_cards.sprites():
        #                     sprite: Card
        #                     if sprite.rect.collidepoint(event.pos[0], event.pos[1]):
        #                         sprite.grab()
        #                         grabbed = sprite
        #                         break
        #         if event.button == 3:
        #             if grabbed is not None:
        #                 grabbed.flip()
        #
        #     if event.type == pg.MOUSEMOTION:
        #         if grabbed is not None:
        #             grabbed.move(event.rel)
        #     if event.type == pg.MOUSEWHEEL:
        #         if grabbed is not None:
        #             grabbed.spin(event.y * 5)
        #
        # debug_card = grabbed if grabbed is not None else debug_card
        # circle_cards.update()
        #
        # moving_cards.empty()
        # for card in card_list:
        #     if card.state != CardState.REST:
        #         moving_cards.add(card)
        #
        #
        #

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
    PROC_POOL.shutdown()


if __name__ == '__main__':
    freeze_support()
    main()

