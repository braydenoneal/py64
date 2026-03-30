import json
import struct
from typing import Any

from moderngl import Context, Program

from py64.window.render.model.animation.animation import Animation


class Model:
    def __init__(self, ctx: Context, program: Program, path: str):
        self.ctx = ctx
        self.program = program

        self.model_dict: dict[str, Any] = {}

        with open(path) as file:
            self.model_dict = json.load(file)

        self.animation = Animation(self.model_dict['bones'])
        self.animation.set_bone_matrices(10)

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

        for face in self.model_dict['faces']:
            for name in ('a', 'b', 'c'):
                vertex = face[name]

                bone_indices = [-1, -1, -1, -1]
                weights = [0.0, 0.0, 0.0, 0.0]

                if 'weights' in vertex.keys():
                    for index, weight in enumerate(vertex['weights']):
                        bone_indices[index] = list(self.model_dict['bones'].keys()).index(weight['bone'])
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
