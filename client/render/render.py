import math

import moderngl
import pygame
from pyglm import glm
from pyglm.glm import vec3

from client.render.collision import collide
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
            vertex_shader="""
                #version 330 core

                uniform mat4 camera;

                in vec3 in_vertex;
                in vec3 in_normal;
                in int in_collides;

                out vec3 normal;
                flat out int collides;

                void main() {
                    gl_Position = camera * vec4(in_vertex, 1);

                    normal = in_normal;
                    collides = in_collides;
                }
            """,
            fragment_shader="""
                #version 330 core

                uniform vec3 color;
                uniform vec3 light;

                in vec3 normal;
                flat in int collides;

                out vec4 out_color;

                void main() {
                    out_color = vec4(color, 1);

                    float lum = dot(normalize(normal), normalize(light));
                    out_color.rgb *= max(lum, 0.0) * 0.5 + 0.5;

                    if (collides > 0) {
                        out_color = vec4(1, 0, 0, 1);
                    }
                }
            """,
        )

        self.grid = Model(self.ctx, self.program, (0, 1, 0), 'assets/models/grid.obj', 10)
        self.sphere = Model(self.ctx, self.program, (1, 0, 0), 'assets/models/sphere.obj', 1)

    def get_camera_matrix(self):
        perspective = glm.perspective(math.radians(70.0), self.ratio, 0.1, 1000.0)
        translate1 = glm.translate(-self.player.position)
        rotation = self.player.get_rotation_matrix()
        translate = glm.translate(-vec3(0, 0, 16))

        return perspective * translate * rotation * translate1

    def get_player_camera_matrix(self):
        perspective = glm.perspective(math.radians(70.0), self.ratio, 0.1, 1000.0)
        rotation = self.player.get_rotation_matrix()
        translate = glm.translate(-vec3(0, 0, 16))
        y_rotate = glm.rotate(self.player.y_angle + math.radians(180), vec3(0, 1, 0))

        return perspective * translate * rotation * y_rotate

    def main_loop(self):
        self.ctx.clear()

        self.update_collision()

        self.program['light'].write(vec3(0, 1, 0))

        self.program['camera'].write(self.get_camera_matrix())
        self.grid.render()

        self.program['camera'].write(self.get_player_camera_matrix())
        self.sphere.render()

        pygame.display.flip()

    def update_collision(self):
        update = False

        if glm.length(self.player.direction) == 0:
            return

        for index, face in enumerate(self.grid.faces):
            next_collides = False

            collides = collide(face.a, face.b, face.c, face.normal, self.player.position, self.player.direction)

            if collides:
                self.player.position += (collides[1] / glm.length(self.player.direction)) * self.player.direction
                self.player.direction = vec3(0)
                next_collides = True

            if face.collides != next_collides:
                self.grid.faces[index].collides = next_collides
                update = True

        self.player.position += self.player.direction
        self.player.direction = vec3(0)

        if update:
            self.grid.update()
