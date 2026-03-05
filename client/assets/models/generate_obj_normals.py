# Modified from https://github.com/mariliafernandez/objnormals/tree/master
import re
from pathlib import Path

import numpy as np


def calculate_normals(filepath):
    with open(filepath) as obj:
        r = obj.read()

    position_data = read_position(r)
    uv_data = read_uvs(r)
    faces_data = read_faces(r)
    obj_n = obj_normals(position_data, faces_data)
    filename = (filepath.name).split('.')[0]

    write_obj(filename, position_data, uv_data, faces_data, obj_n)


def read_position(r):
    position = list()
    v_re = re.compile('v .*')
    v_lines = v_re.findall(r)

    for line in v_lines:
        elements = line.split()[1:]

        x = float(elements[0])
        y = float(elements[1])
        z = float(elements[2])

        position.append([x, y, z])

    return position


def read_uvs(r):
    position = list()
    v_re = re.compile('vt .*')
    v_lines = v_re.findall(r)

    for line in v_lines:
        elements = line.split()[1:]

        x = float(elements[0])
        y = float(elements[1])
        z = float(elements[2])

        position.append([x, y, z])

    return position


def read_faces(r):
    faces = list()
    f_re = re.compile('f .*')
    f_lines = f_re.findall(r)

    for line in f_lines:
        elements = line.split()[1:]
        v1 = elements[0].split('/')
        v2 = elements[1].split('/')
        v3 = elements[2].split('/')

        v1[0] = int(v1[0]) - 1
        v2[0] = int(v2[0]) - 1
        v3[0] = int(v3[0]) - 1

        faces.append([v1, v2, v3])

    return faces


def obj_normals(position, faces):
    normals = list()

    for f in faces:
        p1 = np.asarray(position[f[0][0]])
        p2 = np.asarray(position[f[1][0]])
        p3 = np.asarray(position[f[2][0]])

        normals.append(normal(p1, p2, p3))

    return normals


def normal(p1, p2, p3):
    v1 = p2 - p1
    v2 = p3 - p1

    n = np.cross(v1, v2)

    return n


def write_obj(filename, positions, uvs, faces, normals):
    v_line = ''
    vt_line = ''
    vn_line = ''
    f_line = ''

    for p in positions:
        v_line = f'{v_line}\nv {p[0]} {p[1]} {p[2]}'

    for u in uvs:
        vt_line = f'{vt_line}\nvt {u[0]} {u[1]} {u[2]}'

    for n in normals:
        vn_line = f'{vn_line}\nvn {n[0]} {n[1]} {n[2]}'

    i = 0
    for f in faces:
        i += 1
        f_line = f'{f_line}\nf {f[0][0] + 1}/{f[0][1]}/{i} {f[1][0] + 1}/{f[1][1]}/{i} {f[2][0] + 1}/{f[2][1]}/{i}'

    out = f'# {filename}_out.obj\n{v_line}\n{vt_line}\n{vn_line}\n{f_line}'

    with open(f'{filename}_out.obj', 'w') as f:
        f.write(out)


calculate_normals(Path('Kokiri Forest.obj'))
