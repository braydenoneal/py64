import struct
from dataclasses import dataclass, astuple

from moderngl import Context, Program
from pyglm.glm import vec3


@dataclass
class Face:
    a: vec3
    b: vec3
    c: vec3
    normal: vec3
    collides: bool

    def __iter__(self):
        return iter(astuple(self))


class Model:
    def __init__(self, ctx: Context, program: Program, color: tuple[float, float, float], path: str, scale: vec3 = vec3(1)):
        self.ctx = ctx
        self.program = program
        self.color = color

        vertices: list[tuple[float, float, float]] = []
        normals: list[tuple[float, float, float]] = []
        faces: list[tuple[tuple[int, int], tuple[int, int], tuple[int, int]]] = []

        with open(path) as file:
            for line in file:
                if line.startswith('v '):
                    items = line.split()[1:]
                    vertices.append((
                        float(items[0]) * scale.x,
                        float(items[1]) * scale.y,
                        float(items[2]) * scale.z,
                    ))
                elif line.startswith('vn '):
                    items = line.split()[1:]
                    normals.append((
                        float(items[0]),
                        float(items[1]),
                        float(items[2]),
                    ))
                elif line.startswith('f '):
                    items = line.split()[1:]

                    face0 = items[0].split('//')
                    face1 = items[1].split('//')
                    face2 = items[2].split('//')

                    faces.append((
                        (int(face0[0]), int(face0[1])),
                        (int(face1[0]), int(face1[1])),
                        (int(face2[0]), int(face2[1])),
                    ))

        self.faces: list[Face] = []

        for (av, an), (bv, bn), (cv, cn) in faces:
            self.faces.append(Face(
                vec3(*vertices[av - 1]),
                vec3(*vertices[bv - 1]),
                vec3(*vertices[cv - 1]),
                vec3(*normals[an - 1]),
                False
            ))

        self.bytes = self.get_bytes()
        self.vbo = self.ctx.buffer(self.bytes)

        self.vao = self.ctx.vertex_array(self.program, [
            (self.vbo, '3f 3f i', 'in_vertex', 'in_normal', 'in_collides'),
        ])

    def get_bytes(self):
        bytes_data = b''

        for a, b, c, normal, collides in self.faces:
            bytes_data += struct.pack('3f 3f i', *a, *normal, collides)
            bytes_data += struct.pack('3f 3f i', *b, *normal, collides)
            bytes_data += struct.pack('3f 3f i', *c, *normal, collides)

        return bytes_data

    def update(self):
        self.bytes = self.get_bytes()
        self.vbo.write(self.bytes)

    def render(self):
        self.program['color'] = self.color
        self.vao.render()
