import math

import moderngl
import pygame
from pyglm import glm
from pyglm.glm import vec3

from client.render.collision import collide, signed_distance_to_plane
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

        self.grid = Model(self.ctx, self.program, (0.5, 0.5, 0.5), 'assets/models/kokiri.obj', vec3(0.04125))
        self.sphere = Model(self.ctx, self.program, (1, 0, 0), 'assets/models/sphere.obj', self.player.scale)

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

        self.collide_and_slide()

        self.program['light'].write(vec3(0, 1, 0))

        self.program['camera'].write(self.get_camera_matrix())
        self.grid.render()

        self.program['camera'].write(self.get_player_camera_matrix())
        self.sphere.render()

        pygame.display.flip()

    def collide_with_world(self, position: vec3, velocity: vec3, gravity: bool = False, iterations: int = 0) -> vec3:
        if iterations > 5 or velocity == vec3(0):
            return position

        minimum_distance = 0.005
        collisions: list[tuple[vec3, float]] = []

        # Get all collisions
        for face in self.grid.faces:
            # Convert vertices and normal to ellipsoid space
            a = face.a / self.player.scale
            b = face.b / self.player.scale
            c = face.c / self.player.scale
            normal = glm.normalize(glm.cross(b - a, c - a))

            collision = collide(a, b, c, normal, position, velocity)

            if collision:
                collisions.append(collision)

        # Move freely if there are no collisions
        if len(collisions) == 0:
            return position + velocity

        # Find the closest collision
        collisions.sort(key=lambda collision: collision[1])
        collision_point, collision_distance = collisions[0]

        base_point = vec3(position)
        destination_point = position + velocity

        # Adjust to move very close to the collision point to avoid precision issues
        if collision_distance >= minimum_distance:
            base_point += glm.normalize(velocity) * (collision_distance - minimum_distance)
            collision_point -= glm.normalize(velocity) * minimum_distance

        # Find the sliding plane
        slide_plane_origin = vec3(collision_point)
        slide_plane_normal = glm.normalize(base_point - collision_point)

        # Only apply gravity on steep slopes
        if gravity and abs(glm.length(vec3(0, 1, 0) - slide_plane_normal)) < 0.5:
            return base_point

        destination_point -= signed_distance_to_plane(slide_plane_normal, slide_plane_origin, destination_point) * slide_plane_normal

        # Find the slide vector
        next_velocity = destination_point - collision_point

        # End recursion if the next move is too small
        if glm.length(next_velocity) < minimum_distance:
            return base_point

        return self.collide_with_world(base_point, next_velocity, gravity, iterations + 1)

    def collide_and_slide(self):
        self.player.position = self.collide_with_world(self.player.position / self.player.scale, self.player.get_direction() / self.player.scale) * self.player.scale
        self.player.position = self.collide_with_world(self.player.position / self.player.scale, vec3(0, -0.2, 0) / self.player.scale, True) * self.player.scale
