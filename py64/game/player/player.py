from dataclasses import dataclass

from pyglm import glm
from pyglm.glm import vec3


@dataclass
class PreviousState:
    grounded: bool
    running: bool


class Player:
    def __init__(self):
        self.position = vec3(0, 9.07, 0)
        self.x_angle: float = 0
        self.y_angle: float = 0
        self.looking_y_angle: float = 0
        self.scale = vec3(0.5, 1.5, 0.5)
        self.speed = 0.125
        self.grounded = True
        self.jump_vector = vec3(0)
        self.running = False
        self.previous_state = PreviousState(self.grounded, self.running)

        self.movement = {
            'forward': False,
            'backward': False,
            'left': False,
            'right': False,
            'up': False,
        }

    def set_previous_state(self):
        self.previous_state.grounded = self.grounded
        self.previous_state.running = self.running

    def get_rotation_matrix(self):
        x_rotate = glm.rotate(-self.x_angle, vec3(1, 0, 0))
        y_rotate = glm.rotate(-self.y_angle, vec3(0, 1, 0))

        return x_rotate * y_rotate

    def get_move(self, move_vector: vec3) -> vec3:
        self.running = True
        self.looking_y_angle = self.y_angle
        return glm.rotate(self.y_angle, vec3(0, 1, 0)) * move_vector

    def get_direction(self):
        direction = vec3(0, 0, 0)
        self.running = False

        if self.movement['forward']:
            direction += self.get_move(vec3(0, 0, -1))

        if self.movement['backward']:
            direction += self.get_move(vec3(0, 0, 1))

        if self.movement['left']:
            direction += self.get_move(vec3(-1, 0, 0))

        if self.movement['right']:
            direction += self.get_move(vec3(1, 0, 0))

        if glm.length(direction) != 0.0:
            direction = glm.normalize(direction) * self.speed

            a = glm.normalize(vec3(direction.x, 0, direction.z))
            b = vec3(0, 0, 1)

            self.looking_y_angle = glm.atan2(a.x * b.z - a.z * b.x, a.x * b.x + a.z * b.z)

        if self.movement['up']:
            direction += self.jump_vector

        return direction

    def process_jump_vector(self):
        if self.movement['up']:
            self.jump_vector *= 0.95

            if self.jump_vector.y < 0.01:
                self.movement['up'] = False
                self.jump_vector = vec3(0)

    def jump(self):
        if self.grounded:
            self.movement['up'] = True
            self.jump_vector = vec3(0, 0.5, 0)
