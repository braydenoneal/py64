import math

from pyglm import glm

SPEED = 0.5


class Player:
    def __init__(self):
        self.x: float = 5
        self.y: float = 0
        self.z: float = 0

        self.x_angle: float = 0
        self.y_angle: float = math.pi / 2

    def get_position_vector(self):
        return glm.vec3(self.x, self.y, self.z)

    def get_rotation_matrix(self):
        x_rotate = glm.rotate(-self.x_angle, glm.vec3(1, 0, 0))
        y_rotate = glm.rotate(-self.y_angle, glm.vec3(0, 1, 0))

        return x_rotate * y_rotate

    def _move(self, move_vector: glm.vec3):
        y_rotate = glm.rotate(self.y_angle, glm.vec3(0, 1, 0))
        translate = glm.translate(y_rotate * move_vector)

        self.x, self.y, self.z = translate * self.get_position_vector()

    def move_forward(self):
        self._move(glm.vec3(0, 0, -SPEED))

    def move_backward(self):
        self._move(glm.vec3(0, 0, SPEED))

    def move_left(self):
        self._move(glm.vec3(-SPEED, 0, 0))

    def move_right(self):
        self._move(glm.vec3(SPEED, 0, 0))

    def move_up(self):
        self.y += SPEED

    def move_down(self):
        self.y -= SPEED
