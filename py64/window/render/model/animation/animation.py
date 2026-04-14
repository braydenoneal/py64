from __future__ import annotations

import struct
from typing import Any

import moderngl
from moderngl import Context
from pyglm.glm import vec3, mat3x3, mat4x4

from py64.window.render.model.animation.bone.bone import Bone, Keyframe, TRANSITION


class Animation:
    def __init__(self, ctx: Context, bones_dict: dict[str, Any], scale: vec3):
        self.ctx = ctx
        self.bones_dict = bones_dict
        self.scale = scale
        self.bones: list[Bone] = []
        self.frame: float = 0

        for name, bone_dict in self.bones_dict.items():
            parent: Bone | None = None

            if 'parent' in bone_dict:
                parent_name = bone_dict['parent']

                for bone in self.bones:
                    if bone.name == parent_name:
                        parent = bone
                        break

            head = vec3(*bone_dict['head']) * scale
            tail = vec3(*bone_dict['tail']) * scale

            keyframes: dict[str, list[Keyframe]] = {}
            self.action_lengths: dict[str, float] = {}

            self.actions: list[str] = [next(iter(bone_dict['frames']))]

            for action, frames in bone_dict['frames'].items():
                keyframes[action] = []
                self.action_lengths[action] = 0

                for frame in frames:
                    keyframes[action].append(Keyframe(
                        frame['frame'],
                        mat3x3(frame['matrix']),
                        vec3(*frame['translation']) * scale,
                    ))

                    if frame['frame'] > self.action_lengths[action]:
                        self.action_lengths[action] = frame['frame']

            self.bones.append(Bone(name, head, tail, parent, keyframes, Keyframe(0, mat3x3(1), vec3(0)), Keyframe(0, mat3x3(1), vec3(0))))

        self.bone_matrices: list[mat4x4] = []
        self.bone_matrices_bytes: bytes = b''
        self.set_bone_matrices(0, self.actions[0])
        self.transition = False
        self.prev_action = self.actions[0]

        self.program = self.ctx.program(
            vertex_shader=open('../assets/shaders/armature/vertex.glsl', 'r').read(),
            fragment_shader=open('../assets/shaders/armature/fragment.glsl', 'r').read(),
        )

        self.vbo = self.ctx.buffer(self.get_armature_bytes())

        self.vao = self.ctx.vertex_array(self.program, [
            (self.vbo, '4f', 'in_vertex'),
        ])

    def set_actions(self, actions: list[str]):
        self.prev_action = self.actions[0]
        self.transition = True
        self.actions = actions
        self.frame = 0

    def step(self):
        self.frame += .5

        if self.transition:
            self.set_bone_matrices(self.frame, self.prev_action, self.actions[0])

            if self.frame > TRANSITION:
                self.transition = False
                self.frame = 0

            return

        if len(self.actions) == 1:
            self.frame %= self.action_lengths[self.actions[0]]
            self.set_bone_matrices(self.frame, self.actions[0])
        else:
            if self.frame >= self.action_lengths[self.actions[0]] + TRANSITION:
                self.actions.pop(0)
                self.frame = 0
                self.set_bone_matrices(self.frame, self.actions[0])
            elif self.frame >= self.action_lengths[self.actions[0]]:
                self.set_bone_matrices(self.frame - self.action_lengths[self.actions[0]], self.actions[0], self.actions[1])
            else:
                self.set_bone_matrices(self.frame, self.actions[0])

    def set_bone_matrices(self, frame: float, action: str, next_action: str | None = None):
        bone_matrices: list[mat4x4] = []

        for bone in self.bones:
            bone_matrices.append(bone.get_matrix(frame, action, next_action))

        for i in range(len(bone_matrices), 100):
            bone_matrices.append(mat4x4(1))

        self.bone_matrices = bone_matrices
        self.bone_matrices_bytes: bytes = self.get_bone_matrices_bytes()

    def get_bone_matrices_bytes(self) -> bytes:
        data = b''

        for matrix in self.bone_matrices:
            data += matrix.to_bytes()

        return data

    def get_armature_bytes(self) -> bytes:
        data = b''

        for bone in self.bones:
            data += struct.pack('4f', *bone.head, float(self.bones.index(bone)))
            data += struct.pack('4f', *bone.tail, float(self.bones.index(bone)))

        return data

    def render_armature(self, camera_matrix: mat4x4):
        self.ctx.disable(moderngl.DEPTH_TEST)

        self.program['camera'].write(camera_matrix)
        self.program['bones'].write(self.bone_matrices_bytes)

        self.vbo.write(self.get_armature_bytes())
        self.vao.render(mode=moderngl.LINES)

        self.ctx.enable(moderngl.DEPTH_TEST)
