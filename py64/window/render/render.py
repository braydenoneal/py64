import math

import moderngl
import pygame
from pyglm import glm
from pyglm.glm import vec3

from py64.game.game import Game
from py64.window.render.model.model import Model


class Render:
    def __init__(self, game: Game, width: int, height: int):
        self.game = game
        self.player = game.player
        self.camera = game.camera
        self.width = width
        self.height = height

        self.ctx = moderngl.get_context()
        self.ctx.enable(moderngl.DEPTH_TEST)
        self.ctx.enable(moderngl.CULL_FACE)

        self.program = self.ctx.program(
            vertex_shader=open('../assets/shaders/main/vertex.glsl', 'r').read(),
            fragment_shader=open('../assets/shaders/main/fragment.glsl', 'r').read(),
        )

        self.forest = Model(self.ctx, self.program, '../assets/models/forest.json', vec3(42))
        self.sphere = Model(self.ctx, self.program, '../assets/models/sphere.json', self.player.scale)

    def get_camera_matrix(self, model_position: vec3 = vec3(0), model_rotation: glm.mat4x4 = glm.mat4x4(1)):
        perspective = glm.perspective(math.radians(70.0), self.width / self.height, 0.1, 1000.0)
        rotation = self.camera.get_rotation_matrix()
        translate = glm.translate(model_position - self.camera.position)

        return perspective * rotation * translate * model_rotation

    def main_loop(self):
        self.ctx.clear()

        self.program['light'].write(vec3(-0.2, 0.55, 0.35))

        self.program['camera'].write(self.get_camera_matrix(
            self.player.position,
            glm.rotate(self.player.y_angle + math.radians(180), vec3(0, 1, 0)),
        ))
        self.sphere.render()

        self.program['camera'].write(self.get_camera_matrix())
        self.forest.render()

        pygame.display.flip()
