import json
import os.path
import struct
from typing import Any

import moderngl
import numpy as np
from PIL import Image
from PIL.Image import Transpose
from moderngl import Context, Program, Texture
from pyglm.glm import vec3


class Model:
    def __init__(self, ctx: Context, program: Program, path: str, scale: vec3 = vec3(1)):
        self.ctx = ctx
        self.program = program

        model_dict: dict[str, Any] = {}

        with open(path) as file:
            model_dict = json.load(file)

        bones_dict: dict[str, Any] = {}

        if 'bones' in model_dict.keys():
            bones_dict = model_dict['bones']

        materials_dict: dict[str, Any] = {}

        if 'materials' in model_dict.keys():
            materials_dict = model_dict['materials']

        self.materials: list[Material] = []
        self.transparent_materials: list[Material] = []

        for material_dict in materials_dict.values():
            material = Material(ctx, program, material_dict, bones_dict, scale)

            if 'transparency' in material_dict:
                self.transparent_materials.append(material)
            else:
                self.materials.append(material)

    def update(self):
        for material in self.materials:
            material.update()

    def render(self):
        for material in self.materials:
            material.render()

    def render_transparent(self):
        for material in self.transparent_materials:
            material.render()


class Material:
    def __init__(self, ctx: Context, program: Program, material_dict: dict[str, Any], bones_dict: dict[str, Any], scale: vec3):
        self.ctx = ctx
        self.program = program
        self.material_dict = material_dict
        self.bones_dict = bones_dict
        self.scale = scale

        self.texture_a: Texture | None = None
        self.texture_b: Texture | None = None

        if 'texture' in self.material_dict.keys():
            self.texture_a = self.create_texture(self.material_dict['texture']['name'])

        if 'texture_b' in self.material_dict.keys():
            self.texture_b = self.create_texture(self.material_dict['texture_b']['name'])

        self.bytes = self.get_bytes()
        self.vbo = self.ctx.buffer(self.bytes)

        self.vao = self.ctx.vertex_array(self.program, [
            (self.vbo, '3f 3f 2f 4f 4i 4f', 'in_vertex', 'in_normal', 'in_uv', 'in_color', 'in_bone_indices', 'in_weights'),
        ])

    def create_texture(self, name: str):
        textures_root = '../assets/textures/'

        path = f'{textures_root}{name}'
        path = path if os.path.isfile(path) else f'{textures_root}missing.png'

        image = Image.open(path).convert('RGBA').transpose(Transpose.FLIP_TOP_BOTTOM)
        image_data = np.array(image, np.uint8).tobytes()

        texture = self.ctx.texture(image.size, 4, image_data)
        texture.filter = (moderngl.NEAREST, moderngl.NEAREST)

        return texture

    def get_bytes(self):
        bytes_data = b''

        for face in self.material_dict['faces']:
            for name in ('a', 'b', 'c'):
                vertex = face[name]

                bone_indices = [-1, -1, -1, -1]
                weights = [0.0, 0.0, 0.0, 0.0]

                if 'weights' in vertex.keys():
                    for index, weight in enumerate(vertex['weights']):
                        bone_indices[index] = list(self.bones_dict.keys()).index(weight['bone'])
                        weights[index] = weight['weight']

                bytes_data += struct.pack(
                    '3f 3f 2f 4f 4i 4f',
                    vertex['x'] * self.scale.x,
                    vertex['y'] * self.scale.y,
                    vertex['z'] * self.scale.z,
                    face['normal']['x'],
                    face['normal']['y'],
                    face['normal']['z'],
                    vertex['u'] if 'texture' in self.material_dict.keys() else 0.0,
                    vertex['v'] if 'texture' in self.material_dict.keys() else 0.0,
                    vertex['color']['r'] if self.material_dict['vertex_colors'] else 1.0,
                    vertex['color']['g'] if self.material_dict['vertex_colors'] else 1.0,
                    vertex['color']['b'] if self.material_dict['vertex_colors'] else 1.0,
                    vertex['color']['a'] if self.material_dict['vertex_colors'] and 'transparency' in self.material_dict.keys() else 1.0,
                    *bone_indices,
                    *weights,
                )

        return bytes_data

    def update(self):
        self.bytes = self.get_bytes()
        self.vbo.write(self.bytes)

    def render(self):
        self.program['solid_color'] = vec3(0)

        self.program['use_texture_a'] = False
        self.program['bounds_a'] = (0, 0)
        self.program['texture_a_scale'] = (1, 1)

        self.program['use_texture_b'] = False
        self.program['bounds_b'] = (0, 0)
        self.program['texture_b_scale'] = (1, 1)

        self.program['texture_b_mix'] = 0

        self.program['texture_a'] = 0
        self.program['texture_b'] = 1

        if self.texture_a:
            self.texture_a.use()

            self.program['use_texture_a'] = True

            texture_dict = self.material_dict['texture']
            bound_options = ('repeat', 'extend', 'clip', 'mirror')

            self.program['bounds_a'] = (
                bound_options.index(texture_dict['bounds']['x']),
                bound_options.index(texture_dict['bounds']['y']),
            )

            self.program['texture_a_scale'] = (
                texture_dict['scale']['x'],
                texture_dict['scale']['y'],
            )
        else:
            solid_color = self.material_dict['solid_color']
            self.program['solid_color'] = vec3(solid_color['r'], solid_color['g'], solid_color['b'])

        if self.texture_b:
            self.texture_b.use(1)

            self.program['use_texture_b'] = True

            texture_dict = self.material_dict['texture_b']
            bound_options = ('repeat', 'extend', 'clip', 'mirror')

            self.program['bounds_b'] = (
                bound_options.index(texture_dict['bounds']['x']),
                bound_options.index(texture_dict['bounds']['y']),
            )

            self.program['texture_b_scale'] = (
                texture_dict['scale']['x'],
                texture_dict['scale']['y'],
            )

            self.program['texture_b_mix'] = texture_dict['mix']

        if self.material_dict['backface_culling']:
            self.ctx.enable(moderngl.CULL_FACE)
        else:
            self.ctx.disable(moderngl.CULL_FACE)

        self.program['translucency'] = 0
        self.program['transparency_mode'] = 0

        if 'transparency' in self.material_dict:
            self.program['translucency'] = self.material_dict['transparency']['translucency']

            if self.material_dict['transparency']['mode'] == 'cutout':
                self.program['transparency_mode'] = 1

        self.program['overlay_color'] = vec3(1)

        if 'overlay_color' in self.material_dict.keys():
            overlay_color = self.material_dict['overlay_color']
            self.program['overlay_color'] = vec3(overlay_color['r'], overlay_color['g'], overlay_color['b'])

        self.vao.render()
