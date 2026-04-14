from __future__ import annotations

from dataclasses import dataclass

from pyglm import glm
from pyglm.glm import vec3, mat3x3, mat4x4

TRANSITION: float = 2


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
    keyframes: dict[str, list[Keyframe]]
    prev_keyframe: Keyframe
    next_keyframe: Keyframe

    def get_matrix(self, frame: float, action: str, next_action: str | None) -> mat4x4:
        if next_action is None:
            for keyframe in self.keyframes[action]:
                if frame >= keyframe.frame:
                    self.prev_keyframe = keyframe
                elif frame <= keyframe.frame:
                    self.next_keyframe = keyframe
                    break

            difference = self.next_keyframe.frame - self.prev_keyframe.frame
            factor = ((frame - self.prev_keyframe.frame) / difference) if difference > 0 else 0
        else:
            self.next_keyframe = self.keyframes[next_action][0]

            factor = frame / TRANSITION

        prev_rotate = glm.quat_cast(self.prev_keyframe.matrix)
        next_rotate = glm.quat_cast(self.next_keyframe.matrix)

        rotate = glm.slerp(prev_rotate, next_rotate, factor)

        prev_translate = self.prev_keyframe.translation
        next_translate = self.next_keyframe.translation

        translate = glm.lerp(prev_translate, next_translate, factor)

        matrix = glm.translate(self.head) @ glm.mat4_cast(rotate) @ glm.translate(translate) @ glm.translate(-self.head)

        if self.parent is not None:
            matrix = self.parent.get_matrix(frame, action, next_action) @ matrix

        return matrix
