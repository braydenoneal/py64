import math

import moderngl
import pygame
from pyglm import glm

from py64.game.game import Game
from py64.window.render.model.model import Model


class Render:
    def __init__(self, game: Game):
        self.game = game
        self.player = game.player
        self.clock = pygame.Clock()

        self.ctx = moderngl.get_context()
        self.screen_size = self.ctx.screen.size
        self.aspect_ratio = self.ctx.screen.width / self.ctx.screen.height

        self.player_model = Model(self.ctx, '../assets/models/player.json')

    def get_camera_matrix(self):
        perspective = glm.perspective(math.radians(70.0), self.aspect_ratio, 0.1, 1000.0)
        rotation = self.player.get_rotation_matrix()
        translate = glm.translate(-self.player.position)

        return perspective * rotation * translate

    def main_loop(self):
        self.ctx.clear()

        self.player_model.render(self.get_camera_matrix())

        self.clock.tick(60)
        pygame.display.flip()
