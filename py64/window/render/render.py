import math

import moderngl
import numpy as np
import pygame
from moderngl import Framebuffer
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

        self.fbo_list: list[Framebuffer] = []
        depth_render_buffer = self.ctx.depth_renderbuffer(self.screen_size)

        for depth_layer in range(5):
            color_texture = self.ctx.texture(self.screen_size, 4)
            color_texture.filter = (moderngl.NEAREST, moderngl.NEAREST)

            depth_texture = self.ctx.texture(self.screen_size, 1, dtype='f4')
            depth_texture.filter = (moderngl.NEAREST, moderngl.NEAREST)

            self.fbo_list.append(self.ctx.framebuffer([
                color_texture,
                depth_texture,
            ], depth_render_buffer))

        # self.depth_render_buffer = self.ctx.depth_renderbuffer(self.screen_size)
        #
        # self.color_texture_0 = self.ctx.texture(self.screen_size, 4)
        # self.color_texture_0.filter = (moderngl.NEAREST, moderngl.NEAREST)
        # self.depth_texture_0 = self.ctx.texture(self.screen_size, 1, dtype='f4')
        # self.depth_texture_0.filter = (moderngl.NEAREST, moderngl.NEAREST)
        #
        # self.fbo0 = self.ctx.framebuffer([
        #     self.color_texture_0,
        #     self.depth_texture_0,
        # ], self.depth_render_buffer)
        #
        # self.color_texture_1 = self.ctx.texture(self.screen_size, 4)
        # self.color_texture_1.filter = (moderngl.NEAREST, moderngl.NEAREST)
        # self.depth_texture_1 = self.ctx.texture(self.screen_size, 1, dtype='f4')
        # self.depth_texture_1.filter = (moderngl.NEAREST, moderngl.NEAREST)
        #
        # self.fbo1 = self.ctx.framebuffer([
        #     self.color_texture_1,
        #     self.depth_texture_1,
        # ], self.depth_render_buffer)
        #
        # self.color_texture_2 = self.ctx.texture(self.screen_size, 4)
        # self.color_texture_2.filter = (moderngl.NEAREST, moderngl.NEAREST)
        # self.depth_texture_2 = self.ctx.texture(self.screen_size, 1, dtype='f4')
        # self.depth_texture_2.filter = (moderngl.NEAREST, moderngl.NEAREST)
        #
        # self.fbo2 = self.ctx.framebuffer([
        #     self.color_texture_2,
        #     self.depth_texture_2,
        # ], self.depth_render_buffer)
        #
        # self.color_texture_3 = self.ctx.texture(self.screen_size, 4)
        # self.color_texture_3.filter = (moderngl.NEAREST, moderngl.NEAREST)
        # self.depth_texture_3 = self.ctx.texture(self.screen_size, 1, dtype='f4')
        # self.depth_texture_3.filter = (moderngl.NEAREST, moderngl.NEAREST)
        #
        # self.fbo3 = self.ctx.framebuffer([
        #     self.color_texture_3,
        #     self.depth_texture_3,
        # ], self.depth_render_buffer)
        #
        # self.color_texture_4 = self.ctx.texture(self.screen_size, 4)
        # self.color_texture_4.filter = (moderngl.NEAREST, moderngl.NEAREST)
        # self.depth_texture_4 = self.ctx.texture(self.screen_size, 1, dtype='f4')
        # self.depth_texture_4.filter = (moderngl.NEAREST, moderngl.NEAREST)
        #
        # self.fbo4 = self.ctx.framebuffer([
        #     self.color_texture_4,
        #     self.depth_texture_4,
        # ], self.depth_render_buffer)

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
        # # Pass 0
        # self.fbo0.use()
        # self.ctx.clear()
        #
        # self.program['pass'] = 0
        #
        # self.program['light'].write(vec3(-0.1, 0.55, 0.35))
        # self.program['screen_size'] = self.screen_size
        #
        # self.program['camera'].write(self.get_camera_matrix(
        #     self.player.position,
        #     glm.rotate(self.player.y_angle + math.radians(180), vec3(0, self.aspect_ratio, 0)),
        # ))
        # self.sphere.render()
        #
        # self.program['camera'].write(self.get_camera_matrix())
        # self.forest.render()

        for index, fbo in enumerate(self.fbo_list):
            fbo.use()
            self.ctx.clear()

            self.program['pass'] = index if index < 2 else 2

            if index == 0:
                self.program['light'].write(vec3(-0.1, 0.55, 0.35))
                self.program['screen_size'] = self.screen_size

                self.program['camera'].write(self.get_camera_matrix(
                    self.player.position,
                    glm.rotate(self.player.y_angle + math.radians(180), vec3(0, self.aspect_ratio, 0)),
                ))
                self.sphere.render()

                self.program['camera'].write(self.get_camera_matrix())
                self.forest.render()
                continue

            self.program['depth_texture0'] = 2
            self.fbo_list[0].color_attachments[1].use(2)

            self.program['depth_texture1'] = 3
            self.fbo_list[index - 1].color_attachments[1].use(3)

            self.forest.render_transparent()

        # # Pass 1
        # self.fbo1.use()
        # self.ctx.clear()
        #
        # self.program['depth_texture0'] = 2
        # self.depth_texture_0.use(2)
        #
        # self.program['pass'] = 1
        # self.forest.render_transparent()
        #
        # # Pass 2
        # self.fbo2.use()
        # self.ctx.clear()
        #
        # self.program['depth_texture0'] = 2
        # self.depth_texture_0.use(2)
        #
        # self.program['depth_texture1'] = 3
        # self.depth_texture_1.use(3)
        #
        # self.program['pass'] = 2
        # self.forest.render_transparent()
        #
        # # Pass 3
        # self.fbo3.use()
        # self.ctx.clear()
        #
        # self.program['depth_texture0'] = 2
        # self.depth_texture_0.use(2)
        #
        # self.program['depth_texture1'] = 3
        # self.depth_texture_2.use(3)
        #
        # self.program['pass'] = 2
        # self.forest.render_transparent()
        #
        # # Pass 4
        # self.fbo4.use()
        # self.ctx.clear()
        #
        # self.program['depth_texture0'] = 2
        # self.depth_texture_0.use(2)
        #
        # self.program['depth_texture1'] = 3
        # self.depth_texture_3.use(3)
        #
        # self.program['pass'] = 2
        # self.forest.render_transparent()

        # Render
        self.ctx.screen.use()
        self.ctx.clear()

        for index, fbo in enumerate(self.fbo_list):
            self.program2[f'in_texture_{index}'] = index
            fbo.color_attachments[0].use(index)

        # self.program2['in_texture_0'] = 0
        # self.color_texture_0.use(0)
        # self.program2['in_texture_1'] = 1
        # self.color_texture_1.use(1)
        # self.program2['in_texture_2'] = 2
        # self.color_texture_2.use(2)
        # self.program2['in_texture_3'] = 3
        # self.color_texture_3.use(3)
        # self.program2['in_texture_4'] = 4
        # self.color_texture_4.use(4)

        self.vao.render()

        pygame.display.flip()
