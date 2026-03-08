import math

from pyglm import glm

SPEED = 0.05


class Player:
    def __init__(self):
        self.x: float = 5
        self.y: float = 0
        self.z: float = 0

        self.x_angle: float = 0
        self.y_angle: float = math.pi / 2

    def get_position_vector(self):
        return glm.vec3(self.x, self.y, self.z)

    def get_rotation_matrix(self):
        x_rotate = glm.rotate(-self.x_angle, glm.vec3(1, 0, 0))
        y_rotate = glm.rotate(-self.y_angle, glm.vec3(0, 1, 0))

        return x_rotate * y_rotate

    def _move(self, move_vector: glm.vec3):
        y_rotate = glm.rotate(self.y_angle, glm.vec3(0, 1, 0))
        translate = glm.translate(y_rotate * move_vector)

        self.x, self.y, self.z = translate * self.get_position_vector()
        # self.collides()

    def move_forward(self):
        self._move(glm.vec3(0, 0, -SPEED))

    def move_backward(self):
        self._move(glm.vec3(0, 0, SPEED))

    def move_left(self):
        self._move(glm.vec3(-SPEED, 0, 0))

    def move_right(self):
        self._move(glm.vec3(SPEED, 0, 0))

    def move_up(self):
        self.y += SPEED

    def move_down(self):
        self.y -= SPEED

    # def collides(self) -> bool:
    #     faces = get_collision_data()
    #
    #     for a, b, c, n in faces:
    #         # Nearest to plane
    #         player_point = self.get_position_vector()
    #         plane_point = glm.vec3(*a)
    #         plane_normal: glm.vec3 = glm.vec3(*n)
    #
    #         v: glm.vec3 = player_point - plane_point
    #         dist: float = glm.dot(v, plane_normal)
    #
    #         nearest_point: glm.vec3 = player_point - dist * plane_normal
    #
    #         # Inside triangle
    #         pa: glm.vec3 = glm.vec3(*a) - nearest_point
    #         pb: glm.vec3 = glm.vec3(*b) - nearest_point
    #         pc: glm.vec3 = glm.vec3(*c) - nearest_point
    #
    #         u: glm.vec3 = glm.cross(pb, pc)
    #         v: glm.vec3 = glm.cross(pc, pa)
    #         w: glm.vec3 = glm.cross(pa, pb)
    #
    #         if glm.dot(u, v) > 0 and glm.dot(u, w) > 0:
    #             if glm.distance(player_point, nearest_point) < 2:
    #                 print("COL")
    #                 print(player_point)
    #                 print(a, b, c)
    #                 print(glm.distance(player_point, nearest_point))
    #
    #     return False
