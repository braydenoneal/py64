import math

import moderngl
import pygame
from pyglm import glm
from pyglm.glm import vec3

from client.render.model.model import Model, Face
from server.world.player.player import Player
from server.world.world import World


def closest_point_on_line(a: vec3, b: vec3, point: vec3) -> vec3:
    ab = b - a

    t = glm.dot(point - a, ab) / glm.dot(ab, ab)
    t = glm.clamp(t, 0, 1)

    return a + t * ab


def get_nearest_point_to_plane(normal: vec3, plane_point: vec3, point: vec3) -> vec3:
    dist: float = glm.dot(point - plane_point, normal)
    return point - dist * normal


def get_nearest_point(face: Face, point: vec3) -> vec3:
    a = vec3(face.a.vx, face.a.vy, face.a.vz)
    b = vec3(face.b.vx, face.b.vy, face.b.vz)
    c = vec3(face.c.vx, face.c.vy, face.c.vz)

    # Nearest to plane
    normal = vec3(face.a.nx, face.a.ny, face.a.nz)
    nearest_point = get_nearest_point_to_plane(normal, a, point)

    # Inside triangle
    pa: vec3 = a - nearest_point
    pb: vec3 = b - nearest_point
    pc: vec3 = c - nearest_point

    u: vec3 = glm.cross(pb, pc)
    v: vec3 = glm.cross(pc, pa)
    w: vec3 = glm.cross(pa, pb)

    if glm.dot(u, v) > 0 and glm.dot(u, w) > 0:
        return nearest_point

    # Outside triangle
    ab = closest_point_on_line(a, b, nearest_point)
    bc = closest_point_on_line(b, c, nearest_point)
    ca = closest_point_on_line(c, a, nearest_point)

    abd = glm.distance(ab, nearest_point)
    bcd = glm.distance(bc, nearest_point)
    cad = glm.distance(ca, nearest_point)

    min_distance = min(min(abd, bcd), cad)

    nearest_point = ab

    if min_distance == bcd:
        nearest_point = bc
    elif min_distance == cad:
        nearest_point = ca

    return nearest_point


def get_collides(face: Face, point: vec3) -> bool:
    return glm.distance(point, get_nearest_point(face, point)) < 1


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

    def update_collision(self, bounces: int = 0):
        # self.player.position += self.player.direction
        # return

        # self.player.y -= 0.025
        update = False
        any_collides = False

        for index, face in enumerate(self.grid.faces):
            # print(self.player.direction)
            collides = face.collides
            next_collides = False

            player_point = self.player.position + self.player.direction

            nearest_point = get_nearest_point(face, player_point)

            if glm.distance(player_point, nearest_point) < 1:
                next_collides = True
                any_collides = True

                if self.player.direction != vec3(0, 0, 0):
                    self.player.position = nearest_point - glm.normalize(self.player.direction)  # * 1.001
                    # print(self.player.position)
                    # print(nearest_point)
                    # print(self.player.direction)
                    # print(glm.normalize(self.player.direction))
                    # print(glm.distance(self.player.position, nearest_point))
                    self.player.direction = vec3(0, 0, 0)

                # normal = vec3(face.a.nx, face.a.ny, face.a.nz)
                # plane_point = vec3(face.a.vx, face.a.vy, face.a.vz)
                #
                # next_plane_point = get_nearest_point_to_plane(normal, plane_point, player_point)
                # prev_plane_point = get_nearest_point_to_plane(normal, plane_point, self.player.prev_pos)
                #
                # self.player.position = self.player.prev_pos + next_plane_point - prev_plane_point
                #
                # if bounces < 10:
                #     self.update_collision(bounces + 1)

            if collides != next_collides:
                self.grid.faces[index].collides = next_collides
                update = True

        if not any_collides:
            self.player.position += self.player.direction
            self.player.direction = vec3(0, 0, 0)

        if update:
            self.grid.update()
