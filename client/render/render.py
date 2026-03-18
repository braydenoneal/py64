import math

import moderngl
import pygame
from pyglm import glm
from pyglm.glm import vec3

from client.render.camera.camera import Camera
from client.render.collision import collide, signed_distance_to_plane
from client.render.model.model import Model
from server.world.player.player import Player
from server.world.world import World


class Render:
    def __init__(self, ratio: float, world: World, player: Player, camera: Camera):
        self.ratio = ratio
        self.world = world
        self.player = player
        self.camera = camera

        self.ctx = moderngl.get_context()
        self.ctx.enable(moderngl.DEPTH_TEST)
        self.ctx.enable(moderngl.CULL_FACE)

        self.program = self.ctx.program(
            vertex_shader=open('assets/shaders/main/vertex.glsl', 'r').read(),
            fragment_shader=open('assets/shaders/main/fragment.glsl', 'r').read(),
        )

        self.forest = Model(self.ctx, self.program, 'assets/models/forest.json', vec3(42))
        self.sphere = Model(self.ctx, self.program, 'assets/models/sphere.json', self.player.scale)

    def collide_with_world(self, position: vec3, velocity: vec3, gravity: bool = False, iterations: int = 0) -> vec3:
        if iterations > 5 or velocity == vec3(0):
            return position

        minimum_distance = 0.005
        collisions: list[tuple[vec3, float]] = []

        # Get all collisions
        for face in self.forest.collision_faces:
            # Convert vertices and normal to ellipsoid space
            a = face.a / self.player.scale
            b = face.b / self.player.scale
            c = face.c / self.player.scale
            normal = glm.normalize(glm.cross(b - a, c - a))

            collision = collide(a, b, c, normal, position, velocity, face.one_sided)

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
            self.player.grounded = True
            return base_point

        destination_point -= signed_distance_to_plane(slide_plane_normal, slide_plane_origin, destination_point) * slide_plane_normal

        # Find the slide vector
        next_velocity = destination_point - collision_point

        # End recursion if the next move is too small
        if glm.length(next_velocity) < minimum_distance:
            return base_point

        return self.collide_with_world(base_point, next_velocity, gravity, iterations + 1)

    def collide_and_slide(self):
        self.player.grounded = False
        self.player.position = self.collide_with_world(self.player.position / self.player.scale, self.player.get_direction() / self.player.scale) * self.player.scale
        self.player.position = self.collide_with_world(self.player.position / self.player.scale, vec3(0, -0.2, 0) / self.player.scale, True) * self.player.scale

    def get_camera_matrix(self, model_position: vec3 = vec3(0), model_rotation: glm.mat4x4 = glm.mat4x4(1)):
        perspective = glm.perspective(math.radians(70.0), self.ratio, 0.1, 1000.0)
        rotation = self.camera.get_rotation_matrix()
        translate = glm.translate(model_position - self.camera.position)

        return perspective * rotation * translate * model_rotation

    def main_loop(self):
        self.ctx.clear()

        if self.camera.free_cam:
            self.camera.position += self.camera.get_direction()
        else:
            self.player.process_jump_vector()
            self.collide_and_slide()
            self.camera.snap_to_player()

        self.program['light'].write(vec3(-0.2, 0.55, 0.35))

        self.program['camera'].write(self.get_camera_matrix(
            self.player.position,
            glm.rotate(self.player.y_angle + math.radians(180), vec3(0, 1, 0)),
        ))
        self.sphere.render()

        self.program['camera'].write(self.get_camera_matrix())
        self.forest.render()

        pygame.display.flip()
