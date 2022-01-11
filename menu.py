import pygame as pg
from typing import Dict, Optional, Tuple
from functools import cached_property
from config import MENU_FONT, ASPECT, PROC_POOL


class Menu:
    def __init__(self):
        self.display = pg.display.get_surface()
        self.screens: Dict[str, "Menu.Screen"] = dict()
        self.curr_screen: Optional["Menu.Screen"] = None
        self.closed = False

    def add_screen(self, screen: "Menu.Screen"):
        self.screens[screen.name] = screen

    def goto_screen(self, name):
        self.curr_screen = self.screens[name]

    def draw(self):
        for button in self.curr_screen.buttons.values():
            button_rect = button.surface.get_rect()
            button_rect.center = button.center
            self.display.blit(button.surface, button_rect)

    def click_at(self, x, y):
        for button in self.curr_screen.buttons.values():
            rect = button.surface.get_rect()
            rect.center = button.center
            if rect.collidepoint(x, y):
                button.action()
                break

    # def close(self):
    #     self.closed = True

    class Screen:
        def __init__(self, name, buttons=None):
            self.name = name
            self.buttons: Dict[str, "Menu.Button"] = dict() if buttons is None else buttons

    class Button:
        def __init__(self, text, font=pg.font.get_default_font(), size=20, center=(0, 0), color=(255, 255, 255),
                     background=None, anti_alias=False, action=lambda: print("NO ACTION SET")):
            self.text = text
            self.font = pg.font.SysFont(font, size)
            self.center = center
            self.color = color
            self.background = background
            self.anti_alias = anti_alias
            self.action = action

        @cached_property
        def surface(self):
            surf = self.font.render(self.text, self.anti_alias, self.color, self.background)
            surf.get_rect().center = self.center
            return surf

        def set_center(self, center):
            self.center = center
            self.surface.get_rect().center = center


class MainMenu(Menu):
    def __init__(self):
        super().__init__()

        # Main Screen
        play_button = self.Button("Play", *MENU_FONT, center=((ASPECT[0]//2), (ASPECT[1]*2//5)))
        quit_button = self.Button("Quit", *MENU_FONT, center=((ASPECT[0]//2), (ASPECT[1]*3//5)))

        main_buttons = {"play": play_button,
                        "quit": quit_button}

        main_screen = self.Screen("main", main_buttons)
        self.add_screen(main_screen)
        self.curr_screen = main_screen


class PauseMenu(Menu):
    def __init__(self):
        super().__init__()

        resume_button = self.Button("Resume", *MENU_FONT, center=((ASPECT[0]//2), (ASPECT[1]*2//5)))
        quit_button = self.Button("Quit", *MENU_FONT, center=((ASPECT[0]//2), (ASPECT[1]*3//5)))
        main_buttons = {"resume": resume_button,
                        "quit": quit_button}
        pause_screen = self.Screen("main", main_buttons)
        self.add_screen(pause_screen)
        self.curr_screen = pause_screen
