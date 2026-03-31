from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from pyglm import glm
from pyglm.glm import vec3, mat4x4, quat


def quat_to_mat4x4(q: quat) -> mat4x4:
    w = q.w
    x = q.x
    y = q.y
    z = q.z

    return mat4x4([
        [1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w), 0],
        [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w), 0],
        [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y), 0],
        [0, 0, 0, 1],
    ])


@dataclass
class Keyframe:
    frame: float
    rotation: quat


class Bone:
    def __init__(self, name: str, head: vec3, parent: Bone | None, keyframes: list[Keyframe]):
        self.name = name
        self.head = head
        self.parent = parent
        self.keyframes = keyframes

    def get_matrix(self, frame: float) -> mat4x4:
        rotate = glm.mat4x4(1)

        for keyframe in self.keyframes:
            if keyframe.frame <= frame:
                rotate = glm.translate(self.head) * glm.mat4_cast(keyframe.rotation) * glm.translate(-self.head)
                # rotate = glm.translate(self.head) * quat_to_mat4x4(keyframe.rotation) * glm.translate(-self.head)

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
                keyframes.append(Keyframe(frame['frame'], quat(*frame['rotation'])))

            self.bones.append(Bone(name, head, parent, keyframes))

        self.bone_matrices: list[mat4x4] = []
        self.bone_matrices_bytes: bytes = b''

    def set_bone_matrices(self, frame: float):
        bone_matrices: list[mat4x4] = []

        for bone in self.bones:
            bone_matrices.append(bone.get_matrix(frame))

        self.bone_matrices = bone_matrices
        self.bone_matrices_bytes: bytes = self.get_bone_matrices_bytes()

    def get_bone_matrices_bytes(self) -> bytes:
        data = b''

        for matrix in self.bone_matrices:
            data += matrix.to_bytes()

        return data
