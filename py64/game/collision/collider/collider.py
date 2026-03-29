import json
from typing import Any

from pyglm import glm
from pyglm.glm import vec3

from py64.game.collision.collision import Face, Plane, Intersect
from py64.game.player.player import Player


class Collider:
    def __init__(self, path: str, scale: vec3 = vec3(1)):
        self.model_dict: dict[str, Any] = {}

        with open(path) as file:
            self.model_dict = json.load(file)

        self.collision_faces: list[Face] = []

        for material in self.model_dict['materials'].values():
            for face in material['faces']:
                self.collision_faces.append(Face(
                    vec3(
                        face['a']['x'] * scale.x,
                        face['a']['y'] * scale.y,
                        face['a']['z'] * scale.z,
                    ),
                    vec3(
                        face['b']['x'] * scale.x,
                        face['b']['y'] * scale.y,
                        face['b']['z'] * scale.z,
                    ),
                    vec3(
                        face['c']['x'] * scale.x,
                        face['c']['y'] * scale.y,
                        face['c']['z'] * scale.z,
                    ),
                    vec3(
                        face['normal']['x'],
                        face['normal']['y'],
                        face['normal']['z'],
                    ),
                    material['backface_culling'],
                ))

    def slide_and_collide(self, player: Player, position: vec3, velocity: vec3, gravity: bool = False, iterations: int = 0) -> vec3:
        if iterations > 5 or velocity == vec3(0):
            return position

        minimum_distance = 0.005
        collisions: list[Intersect] = []

        # Get all collisions
        for face in self.collision_faces:
            # Convert vertices and normal to ellipsoid space
            a = face.a / player.scale
            b = face.b / player.scale
            c = face.c / player.scale
            normal = glm.normalize(glm.cross(b - a, c - a))

            collision = Face(a, b, c, normal, face.one_sided).get_intersect(position, velocity)

            if collision:
                collisions.append(collision)

        # Move freely if there are no collisions
        if len(collisions) == 0:
            return position + velocity

        # Find the closest collision
        collisions.sort(key=lambda x: x.time)

        collision_point = collisions[0].point
        collision_distance = collisions[0].time * glm.length(velocity)

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
            player.grounded = True
            return base_point

        destination_point -= Plane(slide_plane_origin, slide_plane_normal).get_signed_distance(destination_point) * slide_plane_normal

        # Find the slide vector
        next_velocity = destination_point - collision_point

        # End recursion if the next move is too small
        if glm.length(next_velocity) < minimum_distance:
            return base_point

        return self.slide_and_collide(player, base_point, next_velocity, gravity, iterations + 1)
