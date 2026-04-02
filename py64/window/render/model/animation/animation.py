from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from pyglm import glm
from pyglm.glm import vec3, mat4x4


@dataclass
class Keyframe:
    frame: float
    matrix: mat4x4
    matrix_basis: mat4x4
    matrix_channel: mat4x4
    matrix_channel_no_parent: mat4x4
    bone_matrix: mat4x4
    bone_matrix_local: mat4x4


class Bone:
    def __init__(self, name: str, head: vec3, parent: Bone | None, keyframes: list[Keyframe]):
        self.name = name
        self.head = head
        self.parent = parent
        self.keyframes = keyframes

    def get_matrix(self, frame: float) -> mat4x4:
        prev_keyframe = Keyframe(0, mat4x4(1), mat4x4(1), mat4x4(1), mat4x4(1), mat4x4(1), mat4x4(1))
        next_keyframe = Keyframe(0, mat4x4(1), mat4x4(1), mat4x4(1), mat4x4(1), mat4x4(1), mat4x4(1))

        for keyframe in self.keyframes:
            if frame >= keyframe.frame:
                prev_keyframe = keyframe

            elif frame <= keyframe.frame:
                next_keyframe = keyframe

        prev_matrix = prev_keyframe.matrix_channel_no_parent
        next_matrix = next_keyframe.matrix_channel_no_parent

        difference = next_keyframe.frame - prev_keyframe.frame
        factor = ((frame - prev_keyframe.frame) / difference) if difference > 0 else 0

        rot0 = glm.quat_cast(prev_matrix)
        rot1 = glm.quat_cast(next_matrix)

        final_rotation = glm.slerp(rot0, rot1, factor)

        prev_translate = prev_matrix[3]
        next_translate = next_matrix[3]

        final_translate = prev_translate * (1 - factor) + next_translate * factor

        final_matrix = glm.mat4_cast(final_rotation)
        final_matrix[3] = final_translate

        rotate = final_matrix
        # rotate = prev_matrix
        # rotate = glm.translate(self.head) * rotate * glm.translate(-self.head)

        if self.parent is not None:
            rotate = self.parent.get_matrix(frame) * rotate

        return rotate


class Animation:
    def __init__(self, bones_dict: dict[str, Any]):
        self.bones_dict = bones_dict
        self.bones: list[Bone] = []

        for name, bone_dict in self.bones_dict.items():
            parent: Bone | None = None

            if 'parent' in bone_dict:
                parent_name = bone_dict['parent']

                for bone in self.bones:
                    if bone.name == parent_name:
                        parent = bone
                        break

            head = vec3(*bone_dict['head'])

            keyframes: list[Keyframe] = []

            for frame in bone_dict['frames']:
                keyframes.append(Keyframe(
                    frame['frame'],
                    mat4x4(frame['matrix']),
                    mat4x4(frame['matrix_basis']),
                    mat4x4(frame['matrix_channel']),
                    mat4x4(frame['matrix_channel_no_parent']),
                    mat4x4(frame['bone_matrix']),
                    mat4x4(frame['bone_matrix_local']),
                ))

            self.bones.append(Bone(name, head, parent, keyframes))

        self.bone_matrices: list[mat4x4] = []
        self.bone_matrices_bytes: bytes = b''

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
