import json
from dataclasses import dataclass
from typing import Any

from pyglm import glm
from pyglm.glm import vec3

from py64.game.collision.collision import Face, Plane, Intersect
from py64.game.player.player import Player

CELL_SIZE = 10


def vertex_in_cell(vertex: vec3, pos: vec3, size: vec3) -> bool:
    return all([pos[i] <= vertex[i] <= pos[i] + size[i] for i in range(3)])


def face_intersects_cell(face: Face, pos: vec3, size: vec3) -> bool:
    min_x: float = face.a.x
    max_x: float = face.a.x
    min_y: float = face.a.y
    max_y: float = face.a.y
    min_z: float = face.a.z
    max_z: float = face.a.z

    for vertex in (face.b, face.c):
        min_x = min(min_x, vertex.x)
        max_x = max(max_x, vertex.x)
        min_y = min(min_y, vertex.y)
        max_y = max(max_y, vertex.y)
        min_z = min(min_z, vertex.z)
        max_z = max(max_z, vertex.z)

    face_pos = vec3(min_x, min_y, min_z)
    face_size = vec3(max_x - min_x, max_y - min_y, max_z - min_z)

    for i in range(3):
        if face_pos[i] > pos[i] + size[i] or face_pos[i] + face_size[i] < pos[i]:
            return False

    return True


@dataclass
class Cell:
    octant: int
    pos: vec3
    face_indices: list[int]
    children: list[Cell]


class Collider:
    def __init__(self, path: str, scale: vec3 = vec3(1)):
        self.model_dict: dict[str, Any] = {}

        with open(path) as file:
            self.model_dict = json.load(file)

        self.collision_faces: list[Face] = []

        for material in self.model_dict['materials'].values():
            for face in material['faces']:
                self.collision_faces.append(Face(
                    vec3(*face['a']['vertex']) * scale,
                    vec3(*face['b']['vertex']) * scale,
                    vec3(*face['c']['vertex']) * scale,
                    vec3(*face['normal']),
                    material['backface_culling'],
                ))

        v = self.collision_faces[0].a

        min_x: float = v.x
        max_x: float = v.x
        min_y: float = v.y
        max_y: float = v.y
        min_z: float = v.z
        max_z: float = v.z

        for face in self.collision_faces:
            for vertex in (face.a, face.b, face.c):
                min_x = min(min_x, vertex.x)
                max_x = max(max_x, vertex.x)
                min_y = min(min_y, vertex.y)
                max_y = max(max_y, vertex.y)
                min_z = min(min_z, vertex.z)
                max_z = max(max_z, vertex.z)

        pos = vec3(min_x, min_y, min_z)
        self.size = vec3(max_x - min_x, max_y - min_y, max_z - min_z)

        self.root = Cell(0, pos, list(range(len(self.collision_faces))), [])
        self.build_octree(self.root, self.size)

        self.cells: list[tuple[Cell, vec3]] = []

    def build_octree(self, parent: Cell, size: vec3, depth: int = 0):
        for octant in range(8):
            pos = parent.pos + vec3(*[float(b) for b in list(bin(octant)[2:].rjust(3, '0'))]) * size / 2
            face_indices = []

            for face_index in parent.face_indices:
                if face_intersects_cell(self.collision_faces[face_index], pos, size / 2):
                    face_indices.append(face_index)

            if len(face_indices) > 0:
                parent.children.append(Cell(octant, pos, face_indices, []))

        if depth > 2:
            return

        for child in parent.children:
            self.build_octree(child, size / 2, depth + 1)

    def traverse_octree_wide(self, pos: vec3) -> list[int]:
        faces = []

        for x in range(-1, 2):
            for y in range(-1, 2):
                for z in range(-1, 2):
                    faces += list(set(self.traverse_octree(pos + vec3(x, y, z) * 4, self.root, self.size)) - set(faces))

        return faces

    def traverse_octree(self, pos: vec3, parent: Cell, size: vec3) -> list[int]:
        for child in parent.children:
            if vertex_in_cell(pos, child.pos, size / 2):
                return self.traverse_octree(pos, child, size / 2)

        self.cells.append((parent, size))
        return parent.face_indices

    def slide_and_collide(self, player: Player, position: vec3, velocity: vec3, gravity: bool = False, iterations: int = 0) -> vec3:
        if iterations > 5 or velocity == vec3(0):
            return position

        minimum_distance = 0.005
        collisions: list[Intersect] = []

        self.cells = []
        # Get all collisions
        for face_index in self.traverse_octree_wide(position * player.scale):
            face = self.collision_faces[face_index]
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
