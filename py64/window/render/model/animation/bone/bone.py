from __future__ import annotations

from dataclasses import dataclass

from pyglm import glm
from pyglm.glm import vec3, mat3x3, mat4x4


@dataclass
class Keyframe:
    frame: float
    matrix: mat3x3
    translation: vec3


@dataclass
class Bone:
    name: str
    head: vec3
    tail: vec3
    parent: Bone | None
    keyframes: list[Keyframe]

    def get_matrix(self, frame: float) -> mat4x4:
        prev_keyframe = Keyframe(0, mat3x3(1), vec3(0))
        next_keyframe = Keyframe(0, mat3x3(1), vec3(0))

        for keyframe in self.keyframes:
            if frame >= keyframe.frame:
                prev_keyframe = keyframe

            elif frame <= keyframe.frame:
                next_keyframe = keyframe
                break

        difference = next_keyframe.frame - prev_keyframe.frame
        factor = ((frame - prev_keyframe.frame) / difference) if difference > 0 else 0

        prev_rotate = glm.quat_cast(prev_keyframe.matrix)
        next_rotate = glm.quat_cast(next_keyframe.matrix)

        rotate = glm.slerp(prev_rotate, next_rotate, factor)

        prev_translate = prev_keyframe.translation
        next_translate = next_keyframe.translation

        translate = glm.lerp(prev_translate, next_translate, factor)

        matrix = glm.translate(self.head) @ glm.mat4_cast(rotate) @ glm.translate(translate) @ glm.translate(-self.head)

        if self.parent is not None:
            matrix = self.parent.get_matrix(frame) @ matrix

        return matrix
