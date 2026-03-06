import math

import moderngl
import pygame
from pyglm import glm

from client.assets.models.read_model import get_materials
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

                in vec3 vertex;
                // in vec3 in_normal;
                in vec2 in_uv;

                out vec3 normal;
                out vec2 uv;

                void main() {
                    gl_Position = camera * vec4(vertex / 10, 1);

                    // normal = in_normal;
                    normal = vec3(0, 1, 0);
                    uv = in_uv;
                }
            """,
            fragment_shader="""
                #version 330 core

                uniform sampler2D Texture;
                uniform vec3 light;

                in vec3 normal;
                in vec2 uv;

                out vec4 out_color;

                void main() {
                    out_color = texture(Texture, uv);

                    float lum = dot(normalize(normal), normalize(light));
                    out_color.rgb *= max(lum, 0.0) * 0.5 + 0.5;
                }
            """,
        )

        self.materials = get_materials(self.ctx, self.program)

    def get_camera_matrix(self):
        perspective = glm.perspective(math.radians(70.0), self.ratio, 0.1, 1000.0)
        rotation = self.player.get_rotation_matrix()
        translate = glm.translate(-self.player.get_position_vector())

        return perspective * rotation * translate

    def main_loop(self):
        self.ctx.clear()

        self.program['camera'].write(self.get_camera_matrix())
        self.program['light'].write(glm.vec3(0, 1, 0))

        for material in self.materials:
            material.render()

        pygame.display.flip()
