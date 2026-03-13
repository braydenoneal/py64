import math

from pyglm import glm
from pyglm.glm import vec3


def signed_distance_to_plane(plane_normal: vec3, plane_origin: vec3, point: vec3) -> float:
    return (point @ plane_normal) - (
            plane_normal.x * plane_origin.x +
            plane_normal.y * plane_origin.y +
            plane_normal.z * plane_origin.z
    )


def get_plane_intersect_time(plane_normal: vec3, plane_origin: vec3, base_point: vec3, velocity: vec3) -> tuple[float | None, bool]:
    signed_distance = signed_distance_to_plane(plane_normal, plane_origin, base_point)
    denominator = plane_normal @ velocity

    if denominator == 0:
        if abs(signed_distance) < 1:
            return 0, True
        else:
            return None, False

    t0 = (1 - signed_distance) / denominator
    t1 = (-1 - signed_distance) / denominator

    if t0 > t1:
        temp = t1
        t1 = t0
        t0 = temp

    if t0 > 1 or t1 < 0:
        return None, False

    return glm.clamp(t0, 0, 1), False


def get_plane_intersection_point(t0: float, plane_normal: vec3, base_point: vec3, velocity: vec3) -> vec3:
    return base_point - plane_normal + t0 * velocity


def is_point_in_triangle(a: vec3, b: vec3, c: vec3, normal: vec3, point: vec3) -> bool:
    # Nearest to plane
    distance = (point - a) @ normal
    nearest_point = point - distance * normal

    # Inside triangle
    pa = a - nearest_point
    pb = b - nearest_point
    pc = c - nearest_point

    u = glm.cross(pb, pc)
    v = glm.cross(pc, pa)
    w = glm.cross(pa, pb)

    return u @ v > 0 and u @ w > 0


def get_lowest_root(a: float, b: float, c: float, cutoff: float) -> float | None:
    # Check if a solution exists
    determinant = b * b - 4.0 * a * c

    # If determinant is negative it means no solutions.
    if determinant < 0 or a == 0.0:
        return None

    # Calculate the two roots: (if determinant == 0 then x1==x2 but let’s disregard that slight optimization)
    sqrt_d = math.sqrt(determinant)
    r1 = (-b - sqrt_d) / (2.0 * a)
    r2 = (-b + sqrt_d) / (2.0 * a)

    # Sort so x1 <= x2
    if r1 > r2:
        temp = r2
        r2 = r1
        r1 = temp

    # Get the lowest root
    if 0 < r1 < cutoff:
        return r1

    # It is possible that we want x2 - this can happen if x1 < 0
    if 0 < r2 < cutoff:
        return r2

    # No (valid) solutions
    return None


def get_vertex_intersection(point: vec3, current_lowest_time: float, base_point: vec3, velocity: vec3) -> tuple[vec3, float] | None:
    a = velocity @ velocity
    b = 2.0 * (velocity @ (base_point - point))
    c = glm.length2(point - base_point) - 1.0

    x1 = get_lowest_root(a, b, c, current_lowest_time)

    if not x1:
        return None

    return point, x1


def get_line_intersection(p1: vec3, p2: vec3, current_lowest_time: float, base_point: vec3, velocity: vec3) -> tuple[vec3, float] | None:
    edge = p2 - p1
    base_to_vertex = p1 - base_point

    edge_squared_length = glm.length2(edge)
    edge_dot_velocity = edge @ velocity
    edge_dot_base_to_vertex = edge @ base_to_vertex
    velocity_squared_length = glm.length2(velocity)

    a = edge_squared_length * -velocity_squared_length + edge_dot_velocity * edge_dot_velocity
    b = edge_squared_length * (2.0 * (velocity @ base_to_vertex)) - 2.0 * edge_dot_velocity * edge_dot_base_to_vertex
    c = edge_squared_length * (1.0 - glm.length2(base_to_vertex)) + edge_dot_base_to_vertex * edge_dot_base_to_vertex

    x1 = get_lowest_root(a, b, c, current_lowest_time)

    if not x1:
        return None

    line_segment_location = (edge_dot_velocity * x1 - edge_dot_base_to_vertex) / edge_squared_length

    return (p1 + line_segment_location * edge, x1) if 0 <= line_segment_location <= 1 else None


def collide(a: vec3, b: vec3, c: vec3, normal: vec3, base_point: vec3, velocity: vec3) -> tuple[vec3, float] | None:
    """
    Uses:
    - Sphere starting point
    - Sphere velocity vector
    - Triangle points
    - Triangle normal

    Returns:
    - The position where the sphere hits the geometry.
    - The distance along the velocity vector that the sphere must travel before the collision occurs.
    """
    if normal @ glm.normalize(velocity) > 0:
        return None  # Not facing the triangle

    # Get the time that the sphere starts and stops colliding
    time, embedded = get_plane_intersect_time(normal, a, base_point, velocity)

    if time is None:
        return None  # Does not collide

    if not embedded:
        # Get the point where the sphere first intersects with the triangle's plane
        plane_intersection_point = get_plane_intersection_point(time, normal, base_point, velocity)

        # Check if that point is within the triangle bounds
        if is_point_in_triangle(a, b, c, normal, plane_intersection_point):
            # Collides with the inside of the triangle; plane_intersection_point is the collision point
            return plane_intersection_point, time * glm.length(velocity)

    time = 1.0
    intersect: vec3 | None = None

    # Check collision against the vertices
    intersect, time = get_vertex_intersection(a, time, base_point, velocity) or (intersect, time)
    intersect, time = get_vertex_intersection(b, time, base_point, velocity) or (intersect, time)
    intersect, time = get_vertex_intersection(c, time, base_point, velocity) or (intersect, time)

    # Check collision against the edges
    intersect, time = get_line_intersection(a, b, time, base_point, velocity) or (intersect, time)
    intersect, time = get_line_intersection(b, c, time, base_point, velocity) or (intersect, time)
    intersect, time = get_line_intersection(c, a, time, base_point, velocity) or (intersect, time)

    return (intersect, time * glm.length(velocity)) if intersect else None
