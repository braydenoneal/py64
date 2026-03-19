from pyglm.glm import vec3

from py64.game.camera.camera import Camera
from py64.game.collision.collider.collider import Collider
from py64.game.collision.collision import collide_and_slide
from py64.game.player.player import Player


class Game:
    def __init__(self):
        self.running = True
        self.player = Player()
        self.camera = Camera(self.player)

        self.forest = Collider('../assets/models/forest.json', vec3(42))

    def main_loop(self):
        if self.camera.free_cam:
            self.camera.position += self.camera.get_direction()
        else:
            self.player.process_jump_vector()
            collide_and_slide(self.player, self.forest)
            self.camera.snap_to_player()
