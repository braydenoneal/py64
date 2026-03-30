import os
from dataclasses import dataclass

import pygame

from py64.game.game import Game
from py64.window.input.input import Input
from py64.window.render.render import Render

os.environ['SDL_WINDOWS_DPI_AWARENESS'] = 'permonitorv2'


@dataclass
class Window:
    def __init__(self, game: Game):
        self.game = game

        pygame.init()
        pygame.mouse.set_visible(False)
        self.width = 200  # pygame.display.Info().current_w
        self.height = 200  # pygame.display.Info().current_h
        self.surface = pygame.display.set_mode((self.width, self.height), flags=pygame.OPENGL | pygame.DOUBLEBUF, vsync=True)

        self.input = Input(self.game, self.width, self.height)
        self.render = Render(self.game)
