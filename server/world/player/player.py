import math

from pyglm import glm
from pyglm.glm import vec3

SPEED = 2


class Player:
    def __init__(self):
        self.position = vec3(0, 3, 0)
        self.direction = vec3(0, 0, 0)

        self.x_angle: float = 0
        self.y_angle: float = math.pi / 2

    def get_rotation_matrix(self):
        x_rotate = glm.rotate(-self.x_angle, vec3(1, 0, 0))
        y_rotate = glm.rotate(-self.y_angle, vec3(0, 1, 0))

        return x_rotate * y_rotate

    def _move(self, move_vector: vec3):
        y_rotate = glm.rotate(self.y_angle, vec3(0, 1, 0))
        translate = glm.translate(y_rotate * move_vector)

        self.direction = translate * vec3(0, 0, 0)

    def move_forward(self):
        self._move(vec3(0, 0, -SPEED))

    def move_backward(self):
        self._move(vec3(0, 0, SPEED))

    def move_left(self):
        self._move(vec3(-SPEED, 0, 0))

    def move_right(self):
        self._move(vec3(SPEED, 0, 0))

    def move_up(self):
        self.direction = vec3(0, SPEED, 0)

    def move_down(self):
        self.direction = vec3(0, -SPEED, 0)
