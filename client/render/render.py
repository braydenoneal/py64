import math

import moderngl
import pygame
from pyglm import glm

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
        translate1 = glm.translate(-self.player.get_position_vector())
        rotation = self.player.get_rotation_matrix()
        translate = glm.translate(-glm.vec3(0, 0, 16))

        return perspective * translate * rotation * translate1

    def get_player_camera_matrix(self):
        perspective = glm.perspective(math.radians(70.0), self.ratio, 0.1, 1000.0)
        rotation = self.player.get_rotation_matrix()
        translate = glm.translate(-glm.vec3(0, 0, 16))
        y_rotate = glm.rotate(self.player.y_angle + math.radians(180), glm.vec3(0, 1, 0))

        return perspective * translate * rotation * y_rotate

    def main_loop(self):
        self.ctx.clear()

        self.update_collision()

        self.program['light'].write(glm.vec3(0, 1, 0))

        self.program['camera'].write(self.get_camera_matrix())
        self.grid.render()

        self.program['camera'].write(self.get_player_camera_matrix())
        self.sphere.render()

        pygame.display.flip()

    def update_collision(self):
        update = False

        for index, face in enumerate(self.grid.faces):
            a = glm.vec3(face.a.vx, face.a.vy, face.a.vz)
            b = glm.vec3(face.b.vx, face.b.vy, face.b.vz)
            c = glm.vec3(face.c.vx, face.c.vy, face.c.vz)
            collides = face.collides
            next_collides = False

            # Nearest to plane
            n = glm.vec3(face.a.nx, face.a.ny, face.a.nz)
            player_point = self.player.get_position_vector()
            plane_point = glm.vec3(*a)
            plane_normal: glm.vec3 = glm.vec3(*n)

            v: glm.vec3 = player_point - plane_point
            dist: float = glm.dot(v, plane_normal)

            nearest_point: glm.vec3 = player_point - dist * plane_normal

            # Inside triangle
            pa: glm.vec3 = glm.vec3(*a) - nearest_point
            pb: glm.vec3 = glm.vec3(*b) - nearest_point
            pc: glm.vec3 = glm.vec3(*c) - nearest_point

            u: glm.vec3 = glm.cross(pb, pc)
            v: glm.vec3 = glm.cross(pc, pa)
            w: glm.vec3 = glm.cross(pa, pb)

            if glm.dot(u, v) > 0 and glm.dot(u, w) > 0:
                if glm.distance(player_point, nearest_point) < 1:
                    next_collides = True

            if collides != next_collides:
                self.grid.faces[index].collides = next_collides
                update = True

        if update:
            self.grid.update()
