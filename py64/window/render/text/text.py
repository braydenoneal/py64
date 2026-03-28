import math
import struct

import moderngl
import numpy as np
from PIL import Image
from PIL import ImageDraw, ImageFont
from moderngl import Context
from pyglm import glm


class Text:
    def __init__(self, ctx: Context, x: float = 0.0, y: float = 0.0, text: str = ' ', size: float = 4.0):
        self.ctx = ctx
        self.x = x
        self.y = y
        self.text = text
        self.size = size

        self.program = self.ctx.program(
            vertex_shader=open('../assets/shaders/font/vertex.glsl', 'r').read(),
            fragment_shader=open('../assets/shaders/font/fragment.glsl', 'r').read(),
        )

        font_size = 16
        characters = ' !"#$%&\'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~'

        font = ImageFont.truetype('../assets/fonts/font.otf', font_size)
        bounds = [font.getbbox(c) for c in characters]

        self.grid_size = math.ceil(math.sqrt(len(characters)))
        self.max_x = math.ceil(max(bounds, key=lambda c: c[2])[2]) + 1
        self.max_y = math.ceil(max(bounds, key=lambda c: c[3])[3]) + 1
        self.lengths = {c: font.getlength(c) for c in characters}

        image = Image.new('RGBA', (self.grid_size * self.max_x, self.grid_size * self.max_y))
        draw = ImageDraw.Draw(image)

        for index, character in enumerate(characters):
            x = index % self.grid_size * self.max_x
            y = index // self.grid_size * self.max_y

            draw.text((x, y), character, font=font)

        image_data = np.array(image, np.uint8).tobytes()
        self.texture = self.ctx.texture(image.size, 4, image_data)
        self.texture.filter = (moderngl.NEAREST, moderngl.NEAREST)

        self.bytes = self.get_bytes()
        self.vbo = self.ctx.buffer(self.bytes)

        self.vao = self.ctx.vertex_array(self.program, [
            (self.vbo, '3f 2f', 'in_vertex', 'in_uv'),
        ])

    def get_bytes(self) -> bytes:
        bytes_data = b''

        scale = self.size / 1000
        x_offset = 0.0
        y_offset = 0.0

        for c in self.text:
            if c == '\n':
                y_offset += self.max_y * scale
                x_offset = 0.0
                continue

            if c not in self.lengths:
                continue

            length = self.lengths[c] * scale

            x0 = x_offset - 1.0 + self.x * 2
            x1 = x0 + length

            y1 = y_offset - self.y * 2
            y0 = y1 - self.max_y * scale

            index = list(self.lengths.keys()).index(c)

            u0 = float(index % self.grid_size * self.max_x) / (self.grid_size * self.max_x)
            u1 = u0 + self.lengths[c] / (self.grid_size * self.max_x)

            v0 = float(index // self.grid_size * self.max_y) / (self.grid_size * self.max_y)
            v1 = v0 + self.max_y / (self.grid_size * self.max_y)

            bytes_data += struct.pack('3f 2f', x0, y0, 0, u0, v1)
            bytes_data += struct.pack('3f 2f', x1, y0, 0, u1, v1)
            bytes_data += struct.pack('3f 2f', x1, y1, 0, u1, v0)

            bytes_data += struct.pack('3f 2f', x0, y0, 0, u0, v1)
            bytes_data += struct.pack('3f 2f', x1, y1, 0, u1, v0)
            bytes_data += struct.pack('3f 2f', x0, y1, 0, u0, v0)

            x_offset += length

        return bytes_data

    def update(self):
        self.bytes = self.get_bytes()
        self.vbo = self.ctx.buffer(self.bytes)
        self.vao = self.ctx.vertex_array(self.program, [
            (self.vbo, '3f 2f', 'in_vertex', 'in_uv'),
        ])

    def render(self):
        self.texture.use()
        self.program['camera'].write(glm.scale(glm.vec3(1, self.ctx.screen.width / self.ctx.screen.height, 1)))
        self.vao.render()
