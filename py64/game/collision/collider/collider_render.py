import moderngl
from moderngl import Context
from pyglm.glm import vec3, vec4, mat4x4

from py64.game.collision.collider.collider import Collider, Cell


class ColliderRender:
    def __init__(self, ctx: Context, collider: Collider):
        self.ctx = ctx
        self.collider = collider

        self.program = self.ctx.program(
            vertex_shader=open('../assets/shaders/octree/vertex.glsl', 'r').read(),
            fragment_shader=open('../assets/shaders/octree/fragment.glsl', 'r').read(),
        )

        self.octree_bytes = self.get_octree_bytes(self.collider.root, self.collider.size)

        self.vbo = self.ctx.buffer(self.octree_bytes + self.get_octree_collide_bytes())

        self.vao = self.ctx.vertex_array(self.program, [
            (self.vbo, '3f 4f', 'in_vertex', 'in_color'),
        ])

    def get_octree_bytes(self, parent: Cell, size: vec3, data: bytes = b'') -> bytes:
        corners: list[vec3] = [parent.pos + vec3(*[float(b) for b in list(bin(octant)[2:].rjust(3, '0'))]) * size for octant in range(8)]

        for a, b in (
                (0, 1),
                (0, 2),
                (0, 4),
                (1, 5),
                (1, 3),
                (2, 3),
                (2, 6),
                (3, 7),
                (4, 5),
                (4, 6),
                (5, 7),
                (6, 7),
        ):
            data += corners[a].to_bytes()
            data += vec4(1, 0, 0, 1).to_bytes()
            data += corners[b].to_bytes()
            data += vec4(1, 0, 0, 1).to_bytes()

        for child in parent.children:
            data = self.get_octree_bytes(child, size / 2, data)

        return data

    def get_octree_collide_bytes(self) -> bytes:
        data = b''

        for cell, size in self.collider.cells:
            corners: list[vec3] = [cell.pos + vec3(*[float(b) for b in list(bin(octant)[2:].rjust(3, '0'))]) * size for octant in range(8)]

            for a, b in (
                    (0, 1),
                    (0, 2),
                    (0, 4),
                    (1, 5),
                    (1, 3),
                    (2, 3),
                    (2, 6),
                    (3, 7),
                    (4, 5),
                    (4, 6),
                    (5, 7),
                    (6, 7),
            ):
                data += corners[a].to_bytes()
                data += vec4(0, 1, 0, 1).to_bytes()
                data += corners[b].to_bytes()
                data += vec4(0, 1, 0, 1).to_bytes()

        return data

    def render(self, camera_matrix: mat4x4):
        self.program['camera'].write(camera_matrix)
        self.vbo = self.ctx.buffer(self.get_octree_collide_bytes() + self.octree_bytes)
        self.vao = self.ctx.vertex_array(self.program, [
            (self.vbo, '3f 4f', 'in_vertex', 'in_color'),
        ])
        self.vao.render(mode=moderngl.LINES)

    def render_transparent(self, camera_matrix: mat4x4):
        pass

    def step_animation(self):
        pass
