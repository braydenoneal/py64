import json
import struct
from typing import Any

import moderngl
from moderngl import Context
from pyglm.glm import vec3, mat4x4

from py64.window.render.model.animation.animation import Animation


class Model:
    def __init__(self, ctx: Context, path: str, render_skeleton: bool = False):
        self.ctx = ctx
        self.render_skeleton = render_skeleton

        self.program = self.ctx.program(
            vertex_shader=open('../assets/shaders/main/vertex.glsl', 'r').read(),
            fragment_shader=open('../assets/shaders/main/fragment.glsl', 'r').read(),
        )

        self.model_dict: dict[str, Any] = {}

        with open(path) as file:
            self.model_dict = json.load(file)

        self.animation: Animation | None = None
        self.empty_bones = b''.join(mat4x4(1).to_bytes() for _ in range(100))

        if self.model_dict['bones'] != {}:
            self.animation = Animation(self.ctx, self.model_dict['bones'])

        self.bytes = self.get_bytes()
        self.vbo = self.ctx.buffer(self.bytes)

        self.vao = self.ctx.vertex_array(self.program, [
            (self.vbo, '3f 3f 4i 4f', 'in_vertex', 'in_normal', 'in_bone_indices', 'in_weights'),
        ])

    def render(self, camera_matrix: mat4x4):
        self.ctx.enable(moderngl.DEPTH_TEST)
        self.ctx.enable(moderngl.CULL_FACE)

        self.program['light'].write(vec3(-0.1, 0.55, 0.35))
        self.program['camera'].write(camera_matrix)

        if self.animation is not None:
            self.program['animate'] = True
            self.program['bones'].write(self.animation.bone_matrices_bytes)
        else:
            self.program['animate'] = False
            self.program['bones'].write(self.empty_bones)

        self.vao.render()

        if self.animation is not None:
            if self.render_skeleton:
                self.ctx.disable(moderngl.DEPTH_TEST)
                self.animation.render_skeleton(camera_matrix)
                self.ctx.enable(moderngl.DEPTH_TEST)

            self.animation.step()

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
