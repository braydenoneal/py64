import math

import moderngl
import pygame
from pyglm import glm
from pyglm.glm import vec3

from py64.game.game import Game
from py64.window.render.model.model import Model


class Render:
    def __init__(self, game: Game):
        self.game = game
        self.player = game.player

        self.ctx = moderngl.get_context()
        self.screen_size = self.ctx.screen.size
        self.aspect_ratio = self.ctx.screen.width / self.ctx.screen.height

        self.ctx.enable(moderngl.DEPTH_TEST)
        self.ctx.enable(moderngl.CULL_FACE)

        self.program = self.ctx.program(
            vertex_shader=open('../assets/shaders/main/vertex.glsl', 'r').read(),
            fragment_shader=open('../assets/shaders/main/fragment.glsl', 'r').read(),
        )

        # self.sphere = Model(self.ctx, self.program, '../assets/models/animation_test.json')
        self.sphere = Model(self.ctx, self.program, '../assets/models/player2.json')
        self.frame = 0.0

    def get_camera_matrix(self):
        perspective = glm.perspective(math.radians(70.0), self.aspect_ratio, 0.1, 1000.0)
        rotation = self.player.get_rotation_matrix()
        translate = glm.translate(-self.player.position)

        return perspective * rotation * translate

    def main_loop(self):
        self.ctx.clear()

        self.frame += 0.25
        self.frame %= 40.0
        self.sphere.animation.set_bone_matrices(self.frame)

        self.program['light'].write(vec3(-0.1, 0.55, 0.35))

        self.program['camera'].write(self.get_camera_matrix())
        self.sphere.render()

        pygame.display.flip()
