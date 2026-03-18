from pyglm import glm
from pyglm.glm import vec3

from server.world.player.player import Player

SPEED = 0.2


class Camera:
    def __init__(self, player: Player):
        self.player = player
        self.free_cam = False
        self.position = vec3(0)
        self.distance_from_player = vec3(0, 0, 12)

        self.movement = {
            'forward': False,
            'backward': False,
            'left': False,
            'right': False,
            'up': False,
            'down': False,
        }

        self.snap_to_player()

    def get_rotation_matrix(self):
        return self.player.get_rotation_matrix()

    def get_move(self, move_vector: vec3) -> vec3:
        return glm.rotate(self.player.y_angle, vec3(0, 1, 0)) * move_vector

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

    def snap_to_player(self):
        self.position = self.player.position + glm.inverse(self.get_rotation_matrix()) * self.distance_from_player

    def snap_to_player_interpolated(self, player_position: vec3):
        return player_position + glm.inverse(self.get_rotation_matrix()) * self.distance_from_player
