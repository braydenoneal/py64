import math
import struct

import moderngl
import pygame
from pyglm import glm

from client.render.model.model import Model
from server.world.player.player import Player
from server.world.world import World


class Render:
    def __init__(self, ratio: float, world: World, player: Player):
        self.ratio = ratio
        self.world = world
        self.player = player

        self.ctx = moderngl.get_context()
        self.ctx.enable(moderngl.DEPTH_TEST)
        self.ctx.enable(moderngl.CULL_FACE)

        self.program = self.ctx.program(
            vertex_shader="""
                #version 330 core

                uniform mat4 camera;
                uniform float scale;

                in vec3 in_vertex;
                in vec3 in_normal;

                out vec3 normal;

                void main() {
                    gl_Position = camera * vec4(in_vertex * scale, 1);

                    normal = in_normal;
                }
            """,
            fragment_shader="""
                #version 330 core

                uniform vec3 color;
                uniform vec3 light;

                in vec3 normal;

                out vec4 out_color;

                void main() {
                    out_color = vec4(color, 1);

                    float lum = dot(normalize(normal), normalize(light));
                    out_color.rgb *= max(lum, 0.0) * 0.5 + 0.5;
                }
            """,
        )

        self.grid = Model(self.ctx, self.program, (0, 1, 0), 'assets/models/grid.obj')
        self.sphere = Model(self.ctx, self.program, (1, 0, 0), 'assets/models/sphere.obj')

    def get_camera_matrix(self):
        perspective = glm.perspective(math.radians(70.0), self.ratio, 0.1, 1000.0)
        translate1 = glm.translate(-self.player.get_position_vector())
        rotation = self.player.get_rotation_matrix()
        translate = glm.translate(-glm.vec3(0, 0, 16))

        return perspective * translate * rotation * translate1

    def get_player_camera_matrix(self):
        perspective = glm.perspective(math.radians(70.0), self.ratio, 0.1, 1000.0)
        rotation = self.player.get_rotation_matrix()
        translate = glm.translate(-glm.vec3(0, 0, 16))
        y_rotate = glm.rotate(self.player.y_angle + math.radians(180), glm.vec3(0, 1, 0))

        return perspective * translate * rotation * y_rotate

    def main_loop(self):
        self.ctx.clear()

        self.program['light'].write(glm.vec3(0, 1, 0))

        self.program['camera'].write(self.get_camera_matrix())
        self.program['scale'].write(struct.pack('f', 10))
        self.grid.render()

        self.program['camera'].write(self.get_player_camera_matrix())
        self.program['scale'].write(struct.pack('f', 1))
        self.sphere.render()

        pygame.display.flip()
