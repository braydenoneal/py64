import json
import struct
from typing import Any

from moderngl import Context, Program

from py64.window.render.model.animation.animation import Animation


class Model:
    def __init__(self, ctx: Context, program: Program, path: str):
        self.ctx = ctx
        self.program = program

        model_dict: dict[str, Any] = {}

        with open(path) as file:
            model_dict = json.load(file)

        self.materials_dict: dict[str, Any] = {}

        if 'materials' in model_dict.keys():
            self.materials_dict = model_dict['materials']

        self.bones_dict: dict[str, Any] = {}

        if 'bones' in model_dict.keys():
            self.bones_dict = model_dict['bones']

        self.animation = Animation(self.bones_dict)
        self.animation.set_bone_matrices(23.4)

        self.bytes = self.get_bytes()
        self.vbo = self.ctx.buffer(self.bytes)

        self.vao = self.ctx.vertex_array(self.program, [
            (self.vbo, '3f 3f 4i 4f', 'in_vertex', 'in_normal', 'in_bone_indices', 'in_weights'),
        ])

    def render(self):
        self.program['bones'].write(self.animation.bone_matrices_bytes)
        self.vao.render()

    def get_bytes(self):
        bytes_data = b''

        for material_dict in self.materials_dict.values():
            for face in material_dict['faces']:
                for name in ('a', 'b', 'c'):
                    vertex = face[name]

                    bone_indices = [-1, -1, -1, -1]
                    weights = [0.0, 0.0, 0.0, 0.0]

                    if 'weights' in vertex.keys():
                        for index, weight in enumerate(vertex['weights']):
                            bone_indices[index] = list(self.bones_dict.keys()).index(weight['bone'])
                            weights[index] = weight['weight']

                    bytes_data += struct.pack(
                        '3f 3f 4i 4f',
                        vertex['x'],
                        vertex['y'],
                        vertex['z'],
                        face['normal']['x'],
                        face['normal']['y'],
                        face['normal']['z'],
                        *bone_indices,
                        *weights,
                    )

        return bytes_data
