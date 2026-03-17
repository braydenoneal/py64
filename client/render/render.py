import datetime
import math

import moderngl
import pygame
from pyglm import glm
from pyglm.glm import vec3

from client.render.model.model import Model
from server.world.player.player import Player
from server.world.world import World


class Render:
    def __init__(self, ratio: float, world: World, player: Player):
        self.ratio = ratio
        self.world = world
        self.player = player

        self.ctx = moderngl.get_context()
        self.ctx.enable(moderngl.DEPTH_TEST)
        self.ctx.enable(moderngl.CULL_FACE)

        self.program = self.ctx.program(
            vertex_shader=open('assets/shaders/main/vertex.glsl', 'r').read(),
            fragment_shader=open('assets/shaders/main/fragment.glsl', 'r').read(),
        )

        self.forest = Model(self.ctx, self.program, 'assets/models/forest.json', vec3(42))
        self.sphere = Model(self.ctx, self.program, 'assets/models/sphere.json', vec3(1, 1.35, 1))

        self.updates_per_second = 60
        self.frame_microseconds = 100000.0 / self.updates_per_second
        self.last_update = datetime.datetime.now()
        self.prev_position = vec3(self.player.position)
        self.next_position = vec3(self.player.position)

    def get_camera_matrix(self):
        perspective = glm.perspective(math.radians(70.0), self.ratio, 0.1, 1000.0)
        translate1 = glm.translate(-self.player.position)
        rotation = self.player.get_rotation_matrix()
        return perspective * rotation * translate1

    def main_loop(self):
        self.ctx.clear()

        self.player.position += self.player.get_direction()

        self.program['light'].write(vec3(-0.2, 0.55, 0.35))
        self.program['camera'].write(self.get_camera_matrix())

        self.forest.render()
        self.sphere.render()

        pygame.display.flip()
