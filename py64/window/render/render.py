import math

import moderngl
import numpy as np
import pygame
from moderngl import Framebuffer
from pyglm import glm
from pyglm.glm import vec3

from py64.game.game import Game
from py64.window.render.model.model import Model
from py64.window.render.text.text import Text


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

        self.program = self.ctx.program(
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

        data = np.array([
            -1, -1, 0, 0, 0,
            +1, -1, 0, 1, 0,
            +1, +1, 0, 1, 1,
            -1, -1, 0, 0, 0,
            +1, +1, 0, 1, 1,
            -1, +1, 0, 0, 1,
        ]).astype('f4').tobytes()

        self.vbo = self.ctx.buffer(data)

        self.vao = self.ctx.vertex_array(self.program, [
            (self.vbo, '3f 2f', 'in_vertex', 'in_uv'),
        ])

        self.screen_program = self.ctx.program(
            vertex_shader=open('../assets/shaders/main/vertex.glsl', 'r').read(),
            fragment_shader=open('../assets/shaders/main/fragment.glsl', 'r').read(),
        )

        self.forest = Model(self.ctx, self.screen_program, '../assets/models/forest.json', vec3(42))
        self.sphere = Model(self.ctx, self.screen_program, '../assets/models/sphere.json', self.player.scale)

        self.text = Text(self.ctx, 0, 0)

    def get_camera_matrix(self, model_position: vec3 = vec3(0), model_rotation: glm.mat4x4 = glm.mat4x4(1)):
        perspective = glm.perspective(math.radians(70.0), self.aspect_ratio, 0.1, 1000.0)
        rotation = self.camera.get_rotation_matrix()
        translate = glm.translate(model_position - self.camera.position)

        return perspective * rotation * translate * model_rotation

    def main_loop(self):
        self.ctx.enable(moderngl.DEPTH_TEST)
        self.ctx.enable(moderngl.CULL_FACE)
        self.ctx.disable(moderngl.BLEND)

        for index, fbo in enumerate(self.fbo_list):
            fbo.use()
            self.ctx.clear()

            self.screen_program['pass'] = index if index < 2 else 2

            if index == 0:
                self.screen_program['light'].write(vec3(-0.1, 0.55, 0.35))
                self.screen_program['screen_size'] = self.screen_size

                self.screen_program['camera'].write(self.get_camera_matrix(
                    self.player.position,
                    glm.rotate(self.player.y_angle + math.radians(180), vec3(0, self.aspect_ratio, 0)),
                ))
                self.sphere.render()

                self.screen_program['camera'].write(self.get_camera_matrix())
                self.forest.render()
            else:
                self.screen_program['opaque_depth_texture'] = 2
                self.fbo_list[0].color_attachments[1].use(2)

                self.screen_program['previous_layer_depth_texture'] = 3
                self.fbo_list[index - 1].color_attachments[1].use(3)

                self.forest.render_transparent()

        self.ctx.disable(moderngl.DEPTH_TEST)
        self.ctx.disable(moderngl.CULL_FACE)
        self.ctx.enable(moderngl.BLEND)

        self.ctx.screen.use()
        self.ctx.clear()

        for index, fbo in enumerate(self.fbo_list):
            self.program[f'in_texture_{index}'] = index
            fbo.color_attachments[0].use(index)

        self.vao.render()

        self.text.text = '\n'.join(str(round(v, 2)) for v in self.player.position.to_list())
        self.text.update()
        self.text.render()

        pygame.display.flip()
