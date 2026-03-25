import math

import moderngl
import numpy as np
import pygame
from pyglm import glm
from pyglm.glm import vec3

from py64.game.game import Game
from py64.window.render.model.model import Model


class Render:
    def __init__(self, game: Game):
        self.game = game
        self.player = game.player
        self.camera = game.camera

        self.ctx = moderngl.get_context()

        self.ctx.enable(moderngl.DEPTH_TEST)
        self.ctx.enable(moderngl.CULL_FACE)

        self.program2 = self.ctx.program(
            vertex_shader=open('../assets/shaders/test/vertex.glsl', 'r').read(),
            fragment_shader=open('../assets/shaders/test/fragment.glsl', 'r').read(),
        )

        self.color_texture = self.ctx.texture((200, 200), 4)
        self.texture2 = self.ctx.texture((200, 200), 4)
        self.depth_texture = self.ctx.depth_texture((200, 200))
        self.color_texture.filter = (moderngl.NEAREST, moderngl.NEAREST)

        data = np.array([
            -1, -1, 0, 0, 0,
            +1, -1, 0, 1, 0,
            +1, +1, 0, 1, 1,
            -1, -1, 0, 0, 0,
            +1, +1, 0, 1, 1,
            -1, +1, 0, 0, 1,
        ]).astype('f4').tobytes()

        self.vbo = self.ctx.buffer(data)

        self.vao = self.ctx.vertex_array(self.program2, [
            (self.vbo, '3f 2f', 'in_vertex', 'in_uv'),
        ])

        self.fbo = self.ctx.framebuffer([self.color_texture, self.texture2], self.depth_texture)

        self.program = self.ctx.program(
            vertex_shader=open('../assets/shaders/main/vertex.glsl', 'r').read(),
            fragment_shader=open('../assets/shaders/main/fragment.glsl', 'r').read(),
        )

        self.forest = Model(self.ctx, self.program, '../assets/models/forest.json', vec3(42))
        self.sphere = Model(self.ctx, self.program, '../assets/models/sphere.json', self.player.scale)

    def get_camera_matrix(self, model_position: vec3 = vec3(0), model_rotation: glm.mat4x4 = glm.mat4x4(1)):
        perspective = glm.perspective(math.radians(70.0), 1, 0.1, 1000.0)
        rotation = self.camera.get_rotation_matrix()
        translate = glm.translate(model_position - self.camera.position)

        return perspective * rotation * translate * model_rotation

    def main_loop(self):
        self.fbo.use()
        self.ctx.clear()

        self.program['light'].write(vec3(-0.1, 0.55, 0.35))

        self.program['camera'].write(self.get_camera_matrix(
            self.player.position,
            glm.rotate(self.player.y_angle + math.radians(180), vec3(0, 1, 0)),
        ))
        self.sphere.render()

        self.program['camera'].write(self.get_camera_matrix())
        self.forest.render()

        self.ctx.screen.use()
        self.ctx.clear()

        self.color_texture.use()
        self.vao.render()

        pygame.display.flip()
