import json
import struct
from dataclasses import dataclass, astuple
from typing import Any

import moderngl
import numpy as np
from PIL import Image
from PIL.Image import Transpose
from moderngl import Context, Program, Texture
from pyglm.glm import vec3


@dataclass
class Face:
    a: vec3
    b: vec3
    c: vec3
    normal: vec3
    one_sided: bool

    def __iter__(self):
        return iter(astuple(self))


class Model:
    def __init__(self, ctx: Context, program: Program, path: str):
        self.ctx = ctx
        self.program = program

        materials_dict: dict[str, Any] = {}

        with open(path) as file:
            materials_dict = json.load(file)

        self.materials: list[Material] = []

        for material_dict in materials_dict.values():
            self.materials.append(Material(ctx, program, material_dict))

        self.collision_faces: list[Face] = []

        for material in materials_dict.values():
            for face in material['faces']:
                self.collision_faces.append(Face(
                    vec3(
                        face['a']['x'] * 42,
                        face['a']['y'] * 42,
                        face['a']['z'] * 42,
                    ),
                    vec3(
                        face['b']['x'] * 42,
                        face['b']['y'] * 42,
                        face['b']['z'] * 42,
                    ),
                    vec3(
                        face['c']['x'] * 42,
                        face['c']['y'] * 42,
                        face['c']['z'] * 42,
                    ),
                    vec3(
                        face['normal']['x'],
                        face['normal']['y'],
                        face['normal']['z'],
                    ),
                    material['backface_culling'],
                ))

    def update(self):
        for material in self.materials:
            material.update()

    def render(self):
        for material in self.materials:
            material.render()


class Material:
    def __init__(self, ctx: Context, program: Program, material_dict: dict[str, Any]):
        self.ctx = ctx
        self.program = program
        self.material_dict = material_dict

        self.texture: Texture | None = None

        if 'texture' in self.material_dict.keys():
            try:
                image = Image.open(f'assets/textures/{self.material_dict["texture"]["name"]}.bmp').convert('RGBA').transpose(Transpose.FLIP_TOP_BOTTOM)
                image_data = np.array(image, np.uint8).tobytes()
                self.texture = self.ctx.texture(image.size, 4, image_data)
                self.texture.filter = (moderngl.NEAREST, moderngl.NEAREST)
            except:
                try:
                    image = Image.open(f'assets/textures/{self.material_dict["texture"]["name"]}.png').convert('RGBA').transpose(Transpose.FLIP_TOP_BOTTOM)
                    image_data = np.array(image, np.uint8).tobytes()
                    self.texture = self.ctx.texture(image.size, 4, image_data)
                    self.texture.filter = (moderngl.NEAREST, moderngl.NEAREST)
                except:
                    image = Image.open(f'assets/textures/missing.png').convert('RGBA').transpose(Transpose.FLIP_TOP_BOTTOM)
                    image_data = np.array(image, np.uint8).tobytes()
                    self.texture = self.ctx.texture(image.size, 4, image_data)
                    self.texture.filter = (moderngl.NEAREST, moderngl.NEAREST)

        self.bytes = self.get_bytes()
        self.vbo = self.ctx.buffer(self.bytes)

        self.vao = self.ctx.vertex_array(self.program, [
            (self.vbo, '3f 3f 2f 4f', 'in_vertex', 'in_normal', 'in_uv', 'in_color'),
        ])

    def get_bytes(self):
        bytes_data = b''

        for face in self.material_dict['faces']:
            bytes_data += struct.pack(
                '3f 3f 2f 4f',
                face['a']['x'] * 42,
                face['a']['y'] * 42,
                face['a']['z'] * 42,
                face['normal']['x'],
                face['normal']['y'],
                face['normal']['z'],
                face['a']['u'] if 'texture' in self.material_dict.keys() else 0.0,
                face['a']['v'] if 'texture' in self.material_dict.keys() else 0.0,
                face['a']['color']['r'] if self.material_dict['vertex_colors'] else 1.0,
                face['a']['color']['g'] if self.material_dict['vertex_colors'] else 1.0,
                face['a']['color']['b'] if self.material_dict['vertex_colors'] else 1.0,
                face['a']['color']['a'] if self.material_dict['vertex_colors'] and 'transparency' in self.material_dict.keys() else 1.0,
            )

            bytes_data += struct.pack(
                '3f 3f 2f 4f',
                face['b']['x'] * 42,
                face['b']['y'] * 42,
                face['b']['z'] * 42,
                face['normal']['x'],
                face['normal']['y'],
                face['normal']['z'],
                face['b']['u'] if 'texture' in self.material_dict.keys() else 0.0,
                face['b']['v'] if 'texture' in self.material_dict.keys() else 0.0,
                face['b']['color']['r'] if self.material_dict['vertex_colors'] else 1.0,
                face['b']['color']['g'] if self.material_dict['vertex_colors'] else 1.0,
                face['b']['color']['b'] if self.material_dict['vertex_colors'] else 1.0,
                face['b']['color']['a'] if self.material_dict['vertex_colors'] and 'transparency' in self.material_dict.keys() else 1.0,
            )

            bytes_data += struct.pack(
                '3f 3f 2f 4f',
                face['c']['x'] * 42,
                face['c']['y'] * 42,
                face['c']['z'] * 42,
                face['normal']['x'],
                face['normal']['y'],
                face['normal']['z'],
                face['c']['u'] if 'texture' in self.material_dict.keys() else 0.0,
                face['c']['v'] if 'texture' in self.material_dict.keys() else 0.0,
                face['c']['color']['r'] if self.material_dict['vertex_colors'] else 1.0,
                face['c']['color']['g'] if self.material_dict['vertex_colors'] else 1.0,
                face['c']['color']['b'] if self.material_dict['vertex_colors'] else 1.0,
                face['c']['color']['a'] if self.material_dict['vertex_colors'] and 'transparency' in self.material_dict.keys() else 1.0,
            )

        return bytes_data

    def update(self):
        self.bytes = self.get_bytes()
        self.vbo.write(self.bytes)

    def render(self):
        self.program['bounds'] = (0, 0)

        if self.texture:
            self.texture.use()

            self.program['bounds'] = (
                ('repeat', 'extend', 'clip', 'mirror').index(self.material_dict['texture']['bounds']['x']),
                ('repeat', 'extend', 'clip', 'mirror').index(self.material_dict['texture']['bounds']['y']),
            )

        if self.material_dict['backface_culling']:
            self.ctx.enable(moderngl.CULL_FACE)
        else:
            self.ctx.disable(moderngl.CULL_FACE)

        self.program['overlay_color'] = vec3(1)

        if 'overlay_color' in self.material_dict.keys():
            overlay_color = self.material_dict['overlay_color']
            self.program['overlay_color'] = vec3(overlay_color['r'], overlay_color['g'], overlay_color['b'])

        self.vao.render()
