import os

import pygame

from client.input.input import Input
from client.render.camera.camera import Camera
from client.render.render import Render
from server.world.player.player import Player
from server.world.world import World

os.environ['SDL_WINDOWS_DPI_AWARENESS'] = 'permonitorv2'


class Window:
    def __init__(self, world: World, player: Player):
        pygame.init()
        pygame.mouse.set_visible(False)
        self.width = pygame.display.Info().current_w
        self.height = pygame.display.Info().current_h
        self.surface = pygame.display.set_mode((self.width, self.height), flags=pygame.OPENGL | pygame.DOUBLEBUF, vsync=True)
        self.camera = Camera(player)
        self.input = Input(self.width, self.height, player, self.camera)
        self.render = Render(self.width / self.height, world, player, self.camera)

    def main_loop(self):
        running = self.input.main_loop()
        self.render.main_loop()
        return running
