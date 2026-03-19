import math
from dataclasses import dataclass

from pyglm import glm
from pyglm.glm import vec3


@dataclass
class Intersect:
    point: vec3
    time: float
    embedded: bool = False


def get_intersect_time(a: float, b: float, c: float, cutoff: float) -> float | None:
    determinant = b * b - 4.0 * a * c

    if determinant < 0 or a == 0.0:
        return None

    sqrt_d = math.sqrt(determinant)

    time_a = (-b - sqrt_d) / (2.0 * a)
    time_b = (-b + sqrt_d) / (2.0 * a)

    if time_a > time_b:
        temp = time_b
        time_b = time_a
        time_a = temp

    if 0 < time_a < cutoff:
        return time_a

    if 0 < time_b < cutoff:
        return time_b

    return None


def get_vertex_intersect(point: vec3, intersect: Intersect | None, start_point: vec3, velocity: vec3) -> Intersect | None:
    a = velocity @ velocity
    b = 2.0 * (velocity @ (start_point - point))
    c = glm.length2(point - start_point) - 1.0

    time = get_intersect_time(a, b, c, intersect.time if intersect is not None else 1.0)

    if time is None:
        return None

    return Intersect(point, time)


def get_line_intersect(point_a: vec3, point_b: vec3, intersect: Intersect | None, start_point: vec3, velocity: vec3) -> Intersect | None:
    edge = point_b - point_a
    base_to_vertex = point_a - start_point

    edge_squared_length = glm.length2(edge)
    edge_dot_velocity = edge @ velocity
    edge_dot_base_to_vertex = edge @ base_to_vertex
    velocity_squared_length = glm.length2(velocity)

    a = edge_squared_length * -velocity_squared_length + edge_dot_velocity * edge_dot_velocity
    b = edge_squared_length * (2.0 * (velocity @ base_to_vertex)) - 2.0 * edge_dot_velocity * edge_dot_base_to_vertex
    c = edge_squared_length * (1.0 - glm.length2(base_to_vertex)) + edge_dot_base_to_vertex * edge_dot_base_to_vertex

    time = get_intersect_time(a, b, c, intersect.time if intersect is not None else 1.0)

    if time is None:
        return None

    line_segment_location = (edge_dot_velocity * time - edge_dot_base_to_vertex) / edge_squared_length

    if 0 <= line_segment_location <= 1:
        return Intersect(point_a + line_segment_location * edge, time)

    return None


class Plane:
    def __init__(self, origin: vec3, normal: vec3):
        self.origin = vec3(origin)
        self.normal = vec3(normal)

    def get_signed_distance(self, point: vec3) -> float:
        return (point @ self.normal) - (
                self.normal.x * self.origin.x +
                self.normal.y * self.origin.y +
                self.normal.z * self.origin.z
        )

    def get_intersect(self, start_point: vec3, velocity: vec3) -> Intersect | None:
        signed_distance = self.get_signed_distance(start_point)
        denominator = self.normal @ velocity

        if denominator == 0:
            if abs(signed_distance) < 1:
                return Intersect(start_point - self.normal, 0, True)
            else:
                return None

        time_a = (1 - signed_distance) / denominator
        time_b = (-1 - signed_distance) / denominator

        if time_a > time_b:
            temp = time_b
            time_b = time_a
            time_a = temp

        if time_a > 1 or time_b < 0:
            return None

        time = glm.clamp(time_a, 0, 1)
        point = start_point - self.normal + time * velocity

        return Intersect(point, time)


@dataclass
class Face:
    a: vec3
    b: vec3
    c: vec3
    normal: vec3
    one_sided: bool

    def is_point_inside(self, point: vec3) -> bool:
        # Nearest to plane
        distance = (point - self.a) @ self.normal
        nearest_point = point - distance * self.normal

        # Inside triangle
        pa = self.a - nearest_point
        pb = self.b - nearest_point
        pc = self.c - nearest_point

        u = glm.cross(pb, pc)
        v = glm.cross(pc, pa)
        w = glm.cross(pa, pb)

        return u @ v > 0 and u @ w > 0

    def get_intersect(self, start_point: vec3, velocity: vec3) -> Intersect | None:
        if self.one_sided and self.normal @ glm.normalize(velocity) > 0:
            return None  # Not facing the triangle

        # Get the intersection with the face's plane
        intersect = Plane(self.a, self.normal).get_intersect(start_point, velocity)

        if intersect is None:
            return None  # Does not collide

        if not intersect.embedded:
            # Check if the plane intersection point is within the triangle bounds
            if self.is_point_inside(intersect.point):
                return intersect

        intersect = None

        # Check collision against the vertices
        intersect = get_vertex_intersect(self.a, intersect, start_point, velocity) or intersect
        intersect = get_vertex_intersect(self.b, intersect, start_point, velocity) or intersect
        intersect = get_vertex_intersect(self.c, intersect, start_point, velocity) or intersect

        # Check collision against the edges
        intersect = get_line_intersect(self.a, self.b, intersect, start_point, velocity) or intersect
        intersect = get_line_intersect(self.b, self.c, intersect, start_point, velocity) or intersect
        intersect = get_line_intersect(self.c, self.a, intersect, start_point, velocity) or intersect

        return intersect
