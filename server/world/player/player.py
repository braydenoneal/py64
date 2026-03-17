import math

from pyglm import glm
from pyglm.glm import vec3

SPEED = 0.25


class Player:
    def __init__(self):
        self.position = vec3(0, 10, 0)
        self.x_angle: float = 0
        self.y_angle: float = math.pi / 2
        self.scale = vec3(0.75, 1.25, 0.75)
        self.grounded = False
        self.jump_vector = vec3(0)

        self.movement = {
            'forward': False,
            'backward': False,
            'left': False,
            'right': False,
            'up': False,
            'down': False,
        }

    def get_rotation_matrix(self):
        x_rotate = glm.rotate(-self.x_angle, vec3(1, 0, 0))
        y_rotate = glm.rotate(-self.y_angle, vec3(0, 1, 0))

        return x_rotate * y_rotate

    def get_move(self, move_vector: vec3) -> vec3:
        y_rotate = glm.rotate(self.y_angle, vec3(0, 1, 0))
        translate = glm.translate(y_rotate * move_vector)

        return translate * vec3(0, 0, 0)

    def get_direction(self):
        direction = vec3(0, 0, 0)

        if self.movement['forward']:
            direction += self.get_move(vec3(0, 0, -1))

        if self.movement['backward']:
            direction += self.get_move(vec3(0, 0, 1))

        if self.movement['left']:
            direction += self.get_move(vec3(-1, 0, 0))

        if self.movement['right']:
            direction += self.get_move(vec3(1, 0, 0))

        if self.movement['up']:
            direction += self.get_move(vec3(0, 1, 0))

        if self.movement['down']:
            direction += self.get_move(vec3(0, -1, 0))

        if glm.length(direction) != 0.0:
            direction = glm.normalize(direction) * SPEED

        return direction
