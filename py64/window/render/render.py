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
        self.clock = pygame.Clock()

        self.ctx = moderngl.get_context()
        self.screen_size = self.ctx.screen.size
        self.aspect_ratio = self.ctx.screen.width / self.ctx.screen.height

        self.screen_program = self.ctx.program(
            vertex_shader=open('../assets/shaders/screen/vertex.glsl', 'r').read(),
            fragment_shader=open('../assets/shaders/screen/fragment.glsl', 'r').read(),
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

        self.vao = self.ctx.vertex_array(self.screen_program, [
            (self.vbo, '3f 2f', 'in_vertex', 'in_uv'),
        ])

        self.program = self.ctx.program(
            vertex_shader=open('../assets/shaders/main/vertex.glsl', 'r').read(),
            fragment_shader=open('../assets/shaders/main/fragment.glsl', 'r').read(),
        )

        self.forest = Model(self.ctx, self.program, '../assets/models/forest.json', vec3(42))
        self.player_model = Model(self.ctx, self.program, '../assets/models/player.json', vec3(0.19))
        self.ellipsoid = Model(self.ctx, self.program, '../assets/models/ellipsoid.json', self.player.scale)

        self.models = [
            self.forest,
            self.player_model,
            # self.ellipsoid,
        ]

        self.text = Text(self.ctx, 0, 0)

    def get_camera_matrix(self):
        perspective = glm.perspective(math.radians(70.0), self.aspect_ratio, 0.1, 1000.0)
        rotation = self.camera.get_rotation_matrix()
        translate = glm.translate(-self.camera.position)

        return perspective * rotation * translate

    def main_loop(self):
        self.ctx.enable(moderngl.DEPTH_TEST)
        self.ctx.enable(moderngl.CULL_FACE)
        self.ctx.disable(moderngl.BLEND)

        self.player_model.animation.action = 'Run' if self.player.running else 'Idle'

        self.player_model.position = self.player.position + vec3(0, -1.5, 0)
        self.player_model.rotation = glm.rotate(self.player.looking_y_angle + math.radians(180), vec3(0, 1, 0))

        self.ellipsoid.position = vec3(self.player.position)

        for index, fbo in enumerate(self.fbo_list):
            fbo.use()
            self.ctx.clear()

            self.program['pass'] = index if index < 2 else 2

            if index == 0:
                self.program['screen_size'] = self.screen_size

                for model in self.models:
                    model.render(self.get_camera_matrix())
            else:
                self.program['opaque_depth_texture'] = 2
                self.fbo_list[0].color_attachments[1].use(2)

                self.program['previous_layer_depth_texture'] = 3
                self.fbo_list[index - 1].color_attachments[1].use(3)

                for model in self.models:
                    model.render_transparent(self.get_camera_matrix())

        for model in self.models:
            model.step_animation()

        self.ctx.disable(moderngl.DEPTH_TEST)
        self.ctx.disable(moderngl.CULL_FACE)
        self.ctx.enable(moderngl.BLEND)

        self.ctx.screen.use()
        self.ctx.clear()

        for index, fbo in enumerate(self.fbo_list):
            self.screen_program[f'in_texture_{index}'] = index
            fbo.color_attachments[0].use(index)

        self.vao.render()

        self.text.text = '\n'.join(str(round(v, 2)) for v in self.player.position.to_list())
        self.text.update()
        self.text.render()

        self.clock.tick(60)
        pygame.display.flip()
