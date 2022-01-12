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

        fps = font.render(str(int(clock.get_fps())), False, (255, 255, 255))
        fps_rect = fps.get_rect()
        screen.blit(background, (0, 0), fps_rect)
        screen.blit(fps, (0, 0), fps_rect)
        updates.append(fps.get_rect())
        pg.display.update(list(reversed(updates)))
    pg.quit()
    PROC_POOL.shutdown()


if __name__ == '__main__':
    freeze_support()
    main()

