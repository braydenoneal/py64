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
        self.screen_size = self.ctx.screen.size
        self.aspect_ratio = self.ctx.screen.width / self.ctx.screen.height

        self.ctx.enable(moderngl.DEPTH_TEST)
        self.ctx.enable(moderngl.CULL_FACE)

        self.program2 = self.ctx.program(
            vertex_shader=open('../assets/shaders/test/vertex.glsl', 'r').read(),
            fragment_shader=open('../assets/shaders/test/fragment.glsl', 'r').read(),
        )

        self.color_texture = self.ctx.texture(self.screen_size, 4)
        self.color_texture.filter = (moderngl.NEAREST, moderngl.NEAREST)
        self.depth_texture = self.ctx.texture(self.screen_size, 1, dtype='f4')
        self.depth_texture.filter = (moderngl.NEAREST, moderngl.NEAREST)

        self.color_texture_0 = self.ctx.texture(self.screen_size, 4)
        self.color_texture_0.filter = (moderngl.NEAREST, moderngl.NEAREST)
        self.depth_texture_0 = self.ctx.texture(self.screen_size, 1, dtype='f4')
        self.depth_texture_0.filter = (moderngl.NEAREST, moderngl.NEAREST)

        self.color_texture_1 = self.ctx.texture(self.screen_size, 1, dtype='f4')
        self.color_texture_1.filter = (moderngl.NEAREST, moderngl.NEAREST)
        self.depth_texture_1 = self.ctx.texture(self.screen_size, 4)
        self.depth_texture_1.filter = (moderngl.NEAREST, moderngl.NEAREST)

        self.fbo = self.ctx.framebuffer([
            self.color_texture,
            self.depth_texture,
        ], self.ctx.depth_renderbuffer(self.screen_size))

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

        self.program = self.ctx.program(
            vertex_shader=open('../assets/shaders/main/vertex.glsl', 'r').read(),
            fragment_shader=open('../assets/shaders/main/fragment.glsl', 'r').read(),
        )

        self.forest = Model(self.ctx, self.program, '../assets/models/forest.json', vec3(42))
        self.sphere = Model(self.ctx, self.program, '../assets/models/sphere.json', self.player.scale)

    def get_camera_matrix(self, model_position: vec3 = vec3(0), model_rotation: glm.mat4x4 = glm.mat4x4(1)):
        perspective = glm.perspective(math.radians(70.0), self.aspect_ratio, 0.1, 1000.0)
        rotation = self.camera.get_rotation_matrix()
        translate = glm.translate(model_position - self.camera.position)

        return perspective * rotation * translate * model_rotation

    def main_loop(self):
        # Pass 0
        self.fbo.use()
        self.ctx.clear()

        self.program['pass'] = 0

        self.program['light'].write(vec3(-0.1, 0.55, 0.35))
        self.program['screen_size'] = self.screen_size

        self.program['camera'].write(self.get_camera_matrix(
            self.player.position,
            glm.rotate(self.player.y_angle + math.radians(180), vec3(0, self.aspect_ratio, 0)),
        ))
        self.sphere.render()

        self.program['camera'].write(self.get_camera_matrix())
        self.forest.render()

        # Write depth texture
        self.depth_texture_0.write(self.depth_texture.read())
        self.program['depth_texture0'] = 2
        self.depth_texture_0.use(2)

        # Pass 1
        self.fbo.use()
        self.ctx.clear()

        self.program['pass'] = 1
        self.forest.render_transparent()

        # # Write depth texture
        # self.depth_texture_1.write(self.depth_texture.read())
        # self.program['depth_texture1'] = 3
        # self.depth_texture_1.use(3)
        #
        # # Pass 2
        # self.fbo.use()
        # self.ctx.clear()
        #
        # self.program['pass'] = 2
        # self.forest.render_transparent()

        # Render
        self.ctx.screen.use()
        self.ctx.clear()

        self.color_texture.use()
        self.vao.render()

        pygame.display.flip()
