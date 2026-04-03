from __future__ import annotations

import struct
from typing import Any

import moderngl
from moderngl import Context
from pyglm.glm import vec3, mat3x3, mat4x4

from py64.window.render.model.animation.bone.bone import Bone, Keyframe


class Animation:
    def __init__(self, ctx: Context, bones_dict: dict[str, Any]):
        self.ctx = ctx
        self.bones_dict = bones_dict
        self.bones: list[Bone] = []
        self.frame: float = 0
        self.last_frame: float = 0

        for name, bone_dict in self.bones_dict.items():
            parent: Bone | None = None

            if 'parent' in bone_dict:
                parent_name = bone_dict['parent']

                for bone in self.bones:
                    if bone.name == parent_name:
                        parent = bone
                        break

            head = vec3(*bone_dict['head'])
            tail = vec3(*bone_dict['tail'])

            keyframes: list[Keyframe] = []

            for frame in bone_dict['frames']:
                keyframes.append(Keyframe(
                    frame['frame'],
                    mat3x3(frame['matrix']),
                ))

                if frame['frame'] > self.last_frame:
                    self.last_frame = frame['frame']

            self.bones.append(Bone(name, head, tail, parent, keyframes))

        self.bone_matrices: list[mat4x4] = []
        self.bone_matrices_bytes: bytes = b''
        self.set_bone_matrices(0)

        self.program = self.ctx.program(
            vertex_shader=open('../assets/shaders/skeleton/vertex.glsl', 'r').read(),
            fragment_shader=open('../assets/shaders/skeleton/fragment.glsl', 'r').read(),
        )

        self.vbo = self.ctx.buffer(self.get_skeleton_bytes())

        self.vao = self.ctx.vertex_array(self.program, [
            (self.vbo, '4f', 'in_vertex'),
        ])

    def step(self):
        self.frame += 1
        self.frame %= self.last_frame
        self.set_bone_matrices(self.frame)

    def set_bone_matrices(self, frame: float):
        bone_matrices: list[mat4x4] = []

        for bone in self.bones:
            bone_matrices.append(bone.get_matrix(frame))

        for i in range(len(bone_matrices), 100):
            bone_matrices.append(mat4x4(1))

        self.bone_matrices = bone_matrices
        self.bone_matrices_bytes: bytes = self.get_bone_matrices_bytes()

    def get_bone_matrices_bytes(self) -> bytes:
        data = b''

        for matrix in self.bone_matrices:
            data += matrix.to_bytes()

        return data

    def get_skeleton_bytes(self) -> bytes:
        data = b''

        for bone in self.bones:
            data += struct.pack('4f', *bone.head, float(self.bones.index(bone)))
            data += struct.pack('4f', *bone.tail, float(self.bones.index(bone)))

        return data

    def render_skeleton(self, camera_matrix: mat4x4):
        self.ctx.disable(moderngl.DEPTH_TEST)

        self.program['camera'].write(camera_matrix)
        self.program['bones'].write(self.bone_matrices_bytes)

        self.vbo.write(self.get_skeleton_bytes())
        self.vao.render(mode=moderngl.LINES)

        self.ctx.enable(moderngl.DEPTH_TEST)
