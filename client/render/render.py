import datetime
import math

import moderngl
import pygame
from pyglm import glm
from pyglm.glm import vec3

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

                in vec3 in_vertex;
                in vec3 in_normal;
                in vec2 in_uv;
                in vec4 in_color;

                out vec3 normal;
                out vec2 uv;
                out vec4 color;

                void main() {
                    gl_Position = camera * vec4(in_vertex, 1);

                    normal = in_normal;
                    uv = in_uv;
                    color = in_color;
                }
            """,
            fragment_shader="""
                #version 330 core

                uniform sampler2D Texture;
                uniform vec3 light;

                in vec3 normal;
                in vec2 uv;
                in vec4 color;

                out vec4 out_color;

                void main() {
                    out_color = texture(Texture, uv);

                    float lum = dot(normalize(normal), normalize(light));
                    out_color.rgb *= max(lum, 0.0) * 0.5 + 0.5;

                    out_color.rgb *= color;
                }
            """,
        )

        self.forest = Model(self.ctx, self.program, 'assets/models/forest.json')

        self.updates_per_second = 60
        self.frame_microseconds = 100000.0 / self.updates_per_second
        self.last_update = datetime.datetime.now()
        self.prev_position = vec3(self.player.position)
        self.next_position = vec3(self.player.position)

    def get_camera_matrix(self):
        perspective = glm.perspective(math.radians(70.0), self.ratio, 0.1, 1000.0)
        translate1 = glm.translate(-self.player.position)
        rotation = self.player.get_rotation_matrix()
        return perspective * rotation * translate1

    def get_player_camera_matrix(self):
        perspective = glm.perspective(math.radians(70.0), self.ratio, 0.1, 1000.0)
        rotation = self.player.get_rotation_matrix()
        translate = glm.translate(-vec3(0, 0, 16))
        y_rotate = glm.rotate(self.player.y_angle + math.radians(180), vec3(0, 1, 0))

        return perspective * translate * rotation * y_rotate

    def main_loop(self):
        self.ctx.clear()

        self.player.position += self.player.get_direction()

        self.program['light'].write(vec3(-0.2, 0.55, 0.35))
        self.program['camera'].write(self.get_camera_matrix())

        self.forest.render()

        pygame.display.flip()
