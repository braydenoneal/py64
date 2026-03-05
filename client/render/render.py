import math

import moderngl
import numpy as np
import pygame
from PIL import Image
from PIL.Image import Transpose
from objloader import Obj
from pyglm import glm

from client.render.texture.texture import TEXTURES
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
                in vec3 in_normal;
                in vec2 in_uv;

                out vec3 normal;
                out vec2 uv;

                void main() {
                    gl_Position = camera * vec4(vertex / 10, 1);

                    normal = in_normal;
                    uv = in_uv;
                }
            """,
            fragment_shader="""
                #version 330 core

                uniform sampler2DArray Texture;
                uniform vec3 light;

                in vec3 normal;
                in vec2 uv;

                out vec4 out_color;

                void main() {
                    out_color = texture(Texture, vec3(uv, 0));

                    float lum = dot(normalize(normal), normalize(light));
                    out_color.rgb *= max(lum, 0.0) * 0.5 + 0.5;
                }
            """,
        )

        obj = Obj.open("assets/models/Kokiri Forest_out.obj")
        self.vbo = self.ctx.buffer(obj.pack('vx vy vz nx ny nz tx ty'))

        self.vao = self.get_vertex_array()

        self.textures = self.get_textures()
        self.textures.filter = (self.ctx.NEAREST, self.ctx.NEAREST)
        self.textures.use()

    def get_vertex_array(self):
        return self.ctx.vertex_array(self.program, [
            (self.vbo, '3f 3f 2f', 'vertex', 'in_normal', 'in_uv'),
        ])

    def get_camera_matrix(self):
        perspective = glm.perspective(math.radians(70.0), self.ratio, 0.1, 1000.0)
        rotation = self.player.get_rotation_matrix()
        translate = glm.translate(-self.player.get_position_vector())

        return perspective * rotation * translate

    def get_textures(self):
        paths = [f"assets/textures/{texture}.png" for texture in TEXTURES]
        images = [Image.open(path).convert('RGBA').transpose(Transpose.FLIP_TOP_BOTTOM) for path in paths]
        image_data = np.array(images, np.uint8)
        return self.ctx.texture_array((16, 16, len(TEXTURES)), 4, image_data.tobytes())

    def main_loop(self):
        self.ctx.clear()

        self.program['camera'].write(self.get_camera_matrix())
        self.program['light'].write(glm.vec3(0, 1, 0))
        self.vao.render()

        pygame.display.flip()
