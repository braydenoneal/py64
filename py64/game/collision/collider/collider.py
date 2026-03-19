import json
from dataclasses import dataclass, astuple
from typing import Any

from pyglm.glm import vec3


@dataclass
class Face:
    a: vec3
    b: vec3
    c: vec3
    normal: vec3
    one_sided: bool

    def __iter__(self):
        return iter(astuple(self))


class Collider:
    def __init__(self, path: str, scale: vec3 = vec3(1)):
        self.materials_dict: dict[str, Any] = {}

        with open(path) as file:
            self.materials_dict = json.load(file)

        self.collision_faces: list[Face] = []

        for material in self.materials_dict.values():
            for face in material['faces']:
                self.collision_faces.append(Face(
                    vec3(
                        face['a']['x'] * scale.x,
                        face['a']['y'] * scale.y,
                        face['a']['z'] * scale.z,
                    ),
                    vec3(
                        face['b']['x'] * scale.x,
                        face['b']['y'] * scale.y,
                        face['b']['z'] * scale.z,
                    ),
                    vec3(
                        face['c']['x'] * scale.x,
                        face['c']['y'] * scale.y,
                        face['c']['z'] * scale.z,
                    ),
                    vec3(
                        face['normal']['x'],
                        face['normal']['y'],
                        face['normal']['z'],
                    ),
                    material['backface_culling'],
                ))
