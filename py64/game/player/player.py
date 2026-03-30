from pyglm import glm
from pyglm.glm import vec3


class Player:
    def __init__(self):
        self.position = vec3(0, 0, 100)
        self.x_angle: float = 0
        self.y_angle: float = 0
        self.speed = 1.2

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
        return glm.rotate(self.y_angle, vec3(0, 1, 0)) * move_vector

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
            direction = glm.normalize(direction) * self.speed

        return direction
