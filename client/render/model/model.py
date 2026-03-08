import struct
from dataclasses import dataclass, astuple

from moderngl import Context, Program


@dataclass
class Vertex:
    vx: float
    vy: float
    vz: float
    nx: float
    ny: float
    nz: float

    def __iter__(self):
        return iter(astuple(self))


@dataclass
class Face:
    a: Vertex
    b: Vertex
    c: Vertex

    def __iter__(self):
        return iter(astuple(self))


class Model:
    def __init__(self, ctx: Context, program: Program, color: tuple[float, float, float], path: str):
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
                        float(items[0]),
                        float(items[1]),
                        float(items[2]),
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
                Vertex(*vertices[av - 1], *normals[an - 1]),
                Vertex(*vertices[bv - 1], *normals[bn - 1]),
                Vertex(*vertices[cv - 1], *normals[cn - 1]),
            ))

        self.bytes = b''

        for a, b, c in self.faces:
            self.bytes += struct.pack('3f 3f', *a)
            self.bytes += struct.pack('3f 3f', *b)
            self.bytes += struct.pack('3f 3f', *c)

        self.vbo = self.ctx.buffer(self.bytes)

        self.vao = self.ctx.vertex_array(self.program, [
            (self.vbo, '3f 3f', 'in_vertex', 'in_normal'),
        ])

    def render(self):
        self.program['color'] = self.color
        self.vao.render()
