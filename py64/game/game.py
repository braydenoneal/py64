from pyglm.glm import vec3

from py64.game.collision.collider.collider import Collider
from py64.game.player.camera.camera import Camera
from py64.game.player.player import Player


class Game:
    def __init__(self):
        self.player = Player()
        self.camera = Camera(self.player)
        self.forest = Collider('../assets/models/forest.json', vec3(42))

    def move_player(self):
        self.player.grounded = False
        self.player.position = self.forest.slide_and_collide(self.player, self.player.position / self.player.scale, self.player.get_direction() / self.player.scale) * self.player.scale
        self.player.position = self.forest.slide_and_collide(self.player, self.player.position / self.player.scale, vec3(0, -0.2, 0) / self.player.scale, True) * self.player.scale

    def main_loop(self):
        if self.camera.free_cam:
            self.camera.position += self.camera.get_direction()
        else:
            self.player.process_jump_vector()
            self.move_player()
            self.camera.snap_to_player()
