import struct

import numpy as np
from PIL import Image
from PIL.Image import Transpose
from moderngl import Context, Program

path = 'client/assets/models/Link Adult.obj'

Material = str
Vertex = tuple[float, float, float]
Normal = tuple[float, float, float]
UV = tuple[float, float]
VertexIndex = int
UVIndex = int
NormalIndex = int
Face = tuple[tuple[VertexIndex, UVIndex, NormalIndex], tuple[VertexIndex, UVIndex, NormalIndex], tuple[VertexIndex, UVIndex, NormalIndex]]

vertices: list[Vertex] = []
uvs: list[UV] = []
normals: list[Normal] = []
materials: dict[Material, list[Face]] = {}

with open(path) as file:
    line = file.readline()
    material = ""

    while line != "":
        if line.startswith("usemtl"):
            material = line.split()[1]

            if material not in materials:
                materials[material] = []

        elif line.startswith("v "):
            items = line.split()[1:]
            vertices.append((float(items[0]) / 1.5, float(items[1]) / 1.5, float(items[2]) / 1.5))

        elif line.startswith("vt "):
            items = line.split()[1:]
            uvs.append((float(items[0]), float(items[1])))

        elif line.startswith("vn "):
            items = line.split()[1:]
            normals.append((float(items[0]), float(items[1]), float(items[2])))

        elif line.startswith("f "):
            items = line.split()[1:]

            face0 = items[0].split('/')
            face1 = items[1].split('/')
            face2 = items[2].split('/')

            materials[material].append((
                (int(face0[0]), int(face0[1]), int(face0[2])),
                (int(face1[0]), int(face1[1]), int(face1[2])),
                (int(face2[0]), int(face2[1]), int(face2[2])),
            ))

        line = file.readline()

VertexData = tuple[Vertex, Normal, UV]
vertex_data: dict[Material, list[VertexData]] = {}

for material, faces in materials.items():
    vertex_data[material] = []

    for face in faces:
        for vertex, uv, normal in face:
            vertex_data[material].append((
                vertices[vertex - 1],
                normals[normal - 1],
                uvs[uv - 1],
            ))


class MaterialData:
    def __init__(self, ctx: Context, program: Program, texture_name: Material, vertex_data: list[VertexData]):
        self.ctx = ctx
        self.program = program
        self.texture_name = texture_name
        self.vertex_data = vertex_data

        image = Image.open(f'client/assets/textures/{texture_name}.png').convert('RGBA').transpose(Transpose.FLIP_TOP_BOTTOM)
        image_data = np.array(image, np.uint8).tobytes()
        self.texture = self.ctx.texture(image.size, 4, image_data)

        self.vbo = self.ctx.buffer(self.vertex_data_to_bytes())

        self.vao = self.ctx.vertex_array(self.program, [
            (self.vbo, '3f 3f 2f', 'vertex', 'in_normal', 'in_uv'),
        ])

    def vertex_data_to_bytes(self) -> bytes:
        data = b''

        for vertex, normal, uv in self.vertex_data:
            data += struct.pack('3f 3f 2f', *vertex, *normal, *uv)

        return data

    def render(self):
        self.texture.use()
        self.vao.render()


def get_materials2(ctx: Context, program: Program) -> list[MaterialData]:
    material_datas: list[MaterialData] = []

    for material, vertex in vertex_data.items():
        material_datas.append(MaterialData(ctx, program, material, vertex))

    return material_datas
