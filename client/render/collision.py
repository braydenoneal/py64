import math

from pyglm import glm
from pyglm.glm import vec3

base_point = vec3(0)
velocity = vec3(0)


def position_at_time(t: float) -> vec3:
    # t ∈ [0, 1]
    return base_point + t * velocity


def signed_distance_to_plane(plane_normal: vec3, plane_origin: vec3, point: vec3) -> float:
    return (point @ plane_normal) - (
            plane_normal.x * plane_origin.x +
            plane_normal.y * plane_origin.y +
            plane_normal.z * plane_origin.z
    )


def get_t0_t1(plane_normal: vec3, plane_origin: vec3) -> tuple[float, float] | None:
    signed_distance = signed_distance_to_plane(plane_normal, plane_origin, base_point)
    denominator = plane_normal @ velocity

    if denominator == 0:
        if abs(signed_distance) < 1:
            return 0, 1
        else:
            return None

    t0 = (1 - signed_distance) / denominator
    t1 = (-1 - signed_distance) / denominator

    return t0, t1


def get_plane_intersection_point(t0: float, plane_normal: vec3) -> vec3:
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


"""
At^2 + Bt + C = 0

A = velocity · velocity
B = 2(velocity · (basePoint − p))
C = ‖p − basePoint‖^2 − 1

x1 = smallest solution (lowest root)

intersectionPoint = p
intersectionDistance = x1‖velocity‖
"""


def get_lowest_root(a: float, b: float, c: float, cutoff: float) -> float | None:
    # Check if a solution exists
    determinant = b * b - 4 * a * c

    # If determinant is negative it means no solutions.
    if determinant < 0:
        return None

    # Calculate the two roots: (if determinant == 0 then x1==x2 but let’s disregard that slight optimization)
    sqrt_d = math.sqrt(determinant)
    r1 = (-b - sqrt_d) / (2 * a)
    r2 = (-b + sqrt_d) / (2 * a)

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


def get_vertex_intersection(point: vec3, current_lowest_time: float) -> tuple[vec3, float] | None:
    a = glm.dot(velocity, velocity)
    b = 2 * (velocity @ (base_point - point))
    c = glm.length(point - base_point) ** 2 - 1

    return get_lowest_root(a, b, c, current_lowest_time)


"""
edge = p2 − p1
baseToVertex = p1 − basePoint

A = ‖edge‖^2 * −‖velocity‖^2 + (edge · velocity)^2
B = ‖edge‖^2 * 2(velocity · baseToVertex) − 2((edge · velocity)(edge · baseToVertex))
C = ‖edge‖^2 * (1 − ‖baseToVertex‖^2) + (edge · baseToVertex)^2

f0 = ((edge · velocity)x1 − (edge · baseToVertex)) / ‖edge‖^2
"""


def get_line_intersection(p1: vec3, p2: vec3, current_lowest_time: float) -> tuple[vec3, float] | None:
    edge = p2 - p1
    base_to_vertex = p1 - base_point

    a = glm.length(edge) ** 2 * -glm.length(velocity) ** 2 + (edge @ velocity) ** 2
    b = glm.length(edge) ** 2 * 2 * (velocity @ base_to_vertex) - 2 * ((edge @ velocity) * (edge @ base_to_vertex))
    c = glm.length(edge) ** 2 * (1 - glm.length(base_to_vertex) ** 2) + (edge @ base_to_vertex) ** 2

    x1 = get_lowest_root(a, b, c, current_lowest_time)

    line_segment_location = ((edge @ velocity) * x1 - (edge @ base_to_vertex)) / glm.length(edge) ** 2

    return p1 + line_segment_location * edge, x1 if 0 <= line_segment_location <= 1 else None


def collide(a: vec3, b: vec3, c: vec3, normal: vec3) -> tuple[vec3, vec3] | None:
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
    # Get the times that the sphere starts and stops colliding
    times = get_t0_t1(normal, a)

    if not times:
        return None  # Does not collide

    t0, t1 = times

    # Next possibilities:
    # - The sphere can collide with the inside of the triangle.
    # - The sphere can collide against one of the three vertices of the triangle.
    # - The sphere can collide against one of the three edges of the triangle.

    # Get the point where the sphere first intersects with the triangle's plane
    plane_intersection_point = get_plane_intersection_point(t0, normal)

    # Check if that point is within the triangle bounds
    if is_point_in_triangle(a, b, c, normal, plane_intersection_point):
        # Collides with the inside of the triangle; plane_intersection_point is the collision point
        return plane_intersection_point, t0 * glm.length(velocity)

    # Check collision against the vertices
    intersect: vec3 | None = None

    intersect, t0 = get_vertex_intersection(a, t0) or intersect, t0
    intersect, t0 = get_vertex_intersection(b, t0) or intersect, t0
    intersect, t0 = get_vertex_intersection(c, t0) or intersect, t0

    intersect, t0 = get_line_intersection(a, b, t0) or intersect, t0
    intersect, t0 = get_line_intersection(b, c, t0) or intersect, t0
    intersect, t0 = get_line_intersection(c, a, t0) or intersect, t0

    if intersect:
        return intersect, t0 * glm.length(velocity)

    return None
