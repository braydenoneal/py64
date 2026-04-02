from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from pyglm import glm
from pyglm.glm import vec3, mat4x4


@dataclass
class Keyframe:
    frame: float
    matrix: mat4x4


class Bone:
    def __init__(self, name: str, head: vec3, parent: Bone | None, keyframes: list[Keyframe]):
        self.name = name
        self.head = head
        self.parent = parent
        self.keyframes = keyframes

    def get_matrix(self, frame: float) -> mat4x4:
        prev_keyframe = Keyframe(0, mat4x4(1))
        next_keyframe = Keyframe(0, mat4x4(1))

        for keyframe in self.keyframes:
            if frame >= keyframe.frame:
                prev_keyframe = keyframe

            elif frame <= keyframe.frame:
                next_keyframe = keyframe

        difference = next_keyframe.frame - prev_keyframe.frame
        factor = ((frame - prev_keyframe.frame) / difference) if difference > 0 else 0

        prev_rotate = glm.quat_cast(prev_keyframe.matrix)
        next_rotate = glm.quat_cast(next_keyframe.matrix)

        rotate = glm.slerp(prev_rotate, next_rotate, factor)

        prev_translate = prev_keyframe.matrix[3]
        next_translate = next_keyframe.matrix[3]

        translate = prev_translate * (1 - factor) + next_translate * factor

        matrix = glm.mat4_cast(rotate)
        matrix[3] = translate

        if self.parent is not None:
            matrix = self.parent.get_matrix(frame) * matrix

        return matrix


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
